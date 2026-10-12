import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Q

from .models import Category, MenuItem, Reservation, Order, OrderItem, Testimonial, DishReview
from .utils import send_reservation_confirmation_email, send_order_receipt_email


def ensure_seeded_data():
    """Auto-seed menu data if the database is currently unpopulated."""
    if not MenuItem.objects.exists():
        from django.core.management import call_command
        try:
            call_command('populate_restaurant')
        except Exception as e:
            print(f"Auto-seed exception: {e}")


@ensure_csrf_cookie
def home(request):
    ensure_seeded_data()
    categories = Category.objects.prefetch_related('items').all()
    featured_items = MenuItem.objects.filter(is_chef_special=True, is_available=True)[:6]
    all_items = MenuItem.objects.filter(is_available=True).select_related('category')
    testimonials = Testimonial.objects.filter(is_featured=True)
    
    seating_choices = Reservation.SEATING_CHOICES
    order_type_choices = Order.ORDER_TYPE_CHOICES

    context = {
        'restaurant_name': "L'Étoile Dorée",
        'tagline': "Michelin-Inspired Contemporary Haute Cuisine",
        'categories': categories,
        'featured_items': featured_items,
        'all_items': all_items,
        'testimonials': testimonials,
        'seating_choices': seating_choices,
        'order_type_choices': order_type_choices,
    }
    return render(request, 'restaurant/index.html', context)


def menu_api(request):
    """API endpoint returning menu items with categories and dietary metadata."""
    ensure_seeded_data()
    category_slug = request.GET.get('category')
    diet = request.GET.get('diet')
    query = request.GET.get('q', '').strip()

    items = MenuItem.objects.filter(is_available=True).select_related('category')

    if category_slug and category_slug != 'all':
        items = items.filter(category__slug=category_slug)

    if diet == 'vegetarian':
        items = items.filter(is_vegetarian=True)
    elif diet == 'vegan':
        items = items.filter(is_vegan=True)
    elif diet == 'gluten_free':
        items = items.filter(is_gluten_free=True)
    elif diet == 'chef_special':
        items = items.filter(is_chef_special=True)

    if query:
        items = items.filter(name__icontains=query) | items.filter(description__icontains=query)

    data = []
    for item in items:
        data.append({
            'id': item.id,
            'name': item.name,
            'slug': item.slug,
            'category_name': item.category.name,
            'category_slug': item.category.slug,
            'description': item.description,
            'price': float(item.price),
            'image_url': item.image_url,
            'calories': item.calories,
            'prep_time': item.prep_time_minutes,
            'rating': float(item.rating),
            'is_vegetarian': item.is_vegetarian,
            'is_vegan': item.is_vegan,
            'is_gluten_free': item.is_gluten_free,
            'is_chef_special': item.is_chef_special,
        })
    return JsonResponse({'items': data})


@csrf_exempt
@require_POST
def reserve_table(request):
    """Handle table reservations via AJAX/JSON."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        name = payload.get('customer_name', '').strip()
        email = payload.get('email', '').strip()
        phone = payload.get('phone', '').strip()
        date = payload.get('date', '').strip()
        time_slot = payload.get('time_slot', '').strip()
        guests = payload.get('guests', 2)
        seating_area = payload.get('seating_area', 'main')
        special_requests = payload.get('special_requests', '').strip()

        if not (name and email and phone and date and time_slot):
            return JsonResponse({'success': False, 'error': 'All mandatory contact and date details are required.'}, status=400)

        reservation = Reservation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            email=email,
            phone=phone,
            date=date,
            time_slot=time_slot,
            guests=int(guests),
            seating_area=seating_area,
            special_requests=special_requests,
            status='confirmed',
        )

        # Dispatch automated HTML confirmation email
        send_reservation_confirmation_email(reservation)

        return JsonResponse({
            'success': True,
            'booking_code': reservation.booking_code,
            'customer_name': reservation.customer_name,
            'date': str(reservation.date),
            'time_slot': reservation.time_slot,
            'guests': reservation.guests,
            'seating_area': reservation.get_seating_area_display(),
            'message': f"Your reservation at L'Étoile Dorée has been confirmed! Confirmation #{reservation.booking_code}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def place_order(request):
    """Handle online culinary orders and return order summary."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = json.loads(request.POST.get('data', '{}'))

        name = payload.get('customer_name', '').strip()
        email = payload.get('email', '').strip()
        phone = payload.get('phone', '').strip()
        order_type = payload.get('order_type', 'dine_in')
        table_or_address = payload.get('table_or_address', '').strip()
        notes = payload.get('notes', '').strip()
        cart_items = payload.get('items', [])

        if not (name and email and phone):
            return JsonResponse({'success': False, 'error': 'Name, email, and phone number are required.'}, status=400)

        if not cart_items:
            return JsonResponse({'success': False, 'error': 'Your tasting cart is empty.'}, status=400)

        subtotal = Decimal('0.00')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            email=email,
            phone=phone,
            order_type=order_type,
            table_or_address=table_or_address,
            notes=notes,
            status='received'
        )

        items_summary = []
        for c_item in cart_items:
            menu_item_id = c_item.get('id')
            qty = int(c_item.get('quantity', 1))
            if qty <= 0:
                continue

            menu_item = get_object_or_404(MenuItem, id=menu_item_id)
            item_total = menu_item.price * qty
            subtotal += item_total

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                item_name=menu_item.name,
                price=menu_item.price,
                quantity=qty,
                item_subtotal=item_total
            )
            items_summary.append({
                'name': menu_item.name,
                'price': float(menu_item.price),
                'quantity': qty,
                'total': float(item_total)
            })

        tip_amount_val = Decimal(str(payload.get('tip_amount', '0.00'))).quantize(Decimal('0.01'))
        payment_method = payload.get('payment_method', 'Credit Card')
        card_number_raw = payload.get('card_number', '').replace(' ', '')
        card_last4 = card_number_raw[-4:] if len(card_number_raw) >= 4 else '4242'

        tax = (subtotal * Decimal('0.085')).quantize(Decimal('0.01'))
        total = subtotal + tax + tip_amount_val

        order.subtotal = subtotal
        order.tax = tax
        order.tip_amount = tip_amount_val
        order.total = total
        order.payment_method = payment_method
        order.card_last4 = card_last4
        order.save()

        # Dispatch automated HTML order receipt email
        send_order_receipt_email(order)

        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'email': order.email,
            'phone': order.phone,
            'order_type': order.get_order_type_display(),
            'table_or_address': order.table_or_address,
            'subtotal': float(subtotal),
            'tax': float(tax),
            'tip_amount': float(tip_amount_val),
            'total': float(total),
            'payment_method': order.payment_method,
            'card_last4': order.card_last4,
            'date': order.created_at.strftime('%B %d, %Y - %H:%M'),
            'items': items_summary,
            'message': f"Payment of ${total:.2f} processed successfully. Order #{order.order_number} confirmed."
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def receipt_view(request, order_number):
    """Render a luxury printable invoice receipt."""
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    return render(request, 'restaurant/receipt.html', {'order': order})


# --- CUSTOMER AUTHENTICATION & PROFILE ---

def register_view(request):
    """Customer registration view."""
    if request.user.is_authenticated:
        return redirect('restaurant:profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not (username and email and password):
            messages.error(request, 'Please complete all required fields.')
            return render(request, 'restaurant/register.html')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'restaurant/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already in use.')
            return render(request, 'restaurant/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'An account with email "{email}" already exists.')
            return render(request, 'restaurant/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f"Welcome to L'Étoile Dorée, {user.first_name or user.username}!")
        return redirect('restaurant:profile')

    return render(request, 'restaurant/register.html')


def login_view(request):
    """Customer login view."""
    if request.user.is_authenticated:
        return redirect('restaurant:profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or request.GET.get('next') or 'restaurant:profile'

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password credentials.')

    return render(request, 'restaurant/login.html')


def logout_view(request):
    """Customer logout view."""
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('restaurant:home')


@login_required(login_url='restaurant:login')
def profile_view(request):
    """Customer portal displaying past reservations and order history."""
    user = request.user
    
    # Query reservations attached to user or matching email
    reservations = Reservation.objects.filter(
        Q(user=user) | Q(email__iexact=user.email)
    ).distinct().order_by('-date', '-created_at')

    # Query orders attached to user or matching email
    orders = Order.objects.filter(
        Q(user=user) | Q(email__iexact=user.email)
    ).prefetch_related('items').distinct().order_by('-created_at')

    context = {
        'user': user,
        'reservations': reservations,
        'orders': orders,
        'total_spent': orders.aggregate(s=Sum('total'))['s'] or Decimal('0.00'),
    }
    return render(request, 'restaurant/profile.html', context)


def admin_dashboard(request):
    """Modern live operational dashboard for staff/managers."""
    reservations = Reservation.objects.all()[:20]
    orders = Order.objects.prefetch_related('items').all()[:20]

    stats = {
        'total_reservations': Reservation.objects.count(),
        'confirmed_reservations': Reservation.objects.filter(status='confirmed').count(),
        'total_orders': Order.objects.count(),
        'revenue': Order.objects.aggregate(rev=Sum('total'))['rev'] or Decimal('0.00'),
        'total_dishes': MenuItem.objects.count(),
    }

    context = {
        'reservations': reservations,
        'orders': orders,
        'stats': stats,
        'status_choices_res': Reservation.STATUS_CHOICES,
        'status_choices_ord': Order.STATUS_CHOICES,
    }
    return render(request, 'restaurant/dashboard.html', context)


@csrf_exempt
@require_POST
def update_status(request):
    """AJAX endpoint to update reservation or order status from dashboard."""
    try:
        data = json.loads(request.body)
        target_type = data.get('type')  # 'reservation' or 'order'
        identifier = data.get('id')
        new_status = data.get('status')

        if target_type == 'reservation':
            res = get_object_or_404(Reservation, booking_code=identifier)
            res.status = new_status
            res.save()
            return JsonResponse({'success': True, 'new_status': res.status, 'display': res.get_status_display()})
        elif target_type == 'order':
            ord_obj = get_object_or_404(Order, order_number=identifier)
            ord_obj.status = new_status
            ord_obj.save()
            return JsonResponse({'success': True, 'new_status': ord_obj.status, 'display': ord_obj.get_status_display()})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid target type.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def dish_reviews_api(request, item_id):
    """Retrieve all approved reviews for a menu item."""
    item = get_object_or_404(MenuItem, id=item_id)
    reviews = item.reviews.filter(is_approved=True)
    reviews_data = []
    for r in reviews:
        reviews_data.append({
            'id': r.id,
            'author_name': r.author_name,
            'rating': r.rating,
            'headline': r.headline,
            'comment': r.comment,
            'date': r.created_at.strftime('%B %d, %Y'),
        })
    return JsonResponse({
        'item': {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'rating': float(item.rating),
            'reviews_count': reviews.count(),
        },
        'reviews': reviews_data,
    })


@csrf_exempt
@require_POST
def submit_dish_review(request):
    """Submit a patron review and recalculate dish rating."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        item_id = payload.get('item_id')
        item = get_object_or_404(MenuItem, id=item_id)

        rating_val = int(payload.get('rating', 5))
        rating_val = max(1, min(5, rating_val))

        headline = payload.get('headline', '').strip()
        comment = payload.get('comment', '').strip()

        if not comment:
            return JsonResponse({'success': False, 'error': 'Review commentary cannot be empty.'}, status=400)

        if request.user.is_authenticated:
            user = request.user
            author_name = user.get_full_name() or user.username
        else:
            user = None
            author_name = payload.get('author_name', '').strip() or 'Esteemed Patron'

        review = DishReview.objects.create(
            menu_item=item,
            user=user,
            author_name=author_name,
            rating=rating_val,
            headline=headline,
            comment=comment,
            is_approved=True,
        )

        # Refresh item to get updated rating
        item.refresh_from_db()

        return JsonResponse({
            'success': True,
            'new_rating': float(item.rating),
            'reviews_count': item.reviews.filter(is_approved=True).count(),
            'review': {
                'id': review.id,
                'author_name': review.author_name,
                'rating': review.rating,
                'headline': review.headline,
                'comment': review.comment,
                'date': review.created_at.strftime('%B %d, %Y'),
            },
            'message': f"Your tasting review for {item.name} has been published!"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

