import uuid
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='utensils', help_text="FontAwesome or Lucide icon keyword")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)
    prep_time_minutes = models.PositiveIntegerField(default=15)
    spice_level = models.PositiveSmallIntegerField(default=0, help_text="0 (mild) to 3 (spicy)")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    
    # Dietary badges
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_chef_special = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_chef_special', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while MenuItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def update_rating(self):
        avg = self.reviews.filter(is_approved=True).aggregate(models.Avg('rating'))['rating__avg']
        if avg is not None:
            self.rating = Decimal(str(round(avg, 1)))
            self.save(update_fields=['rating'])

    def __str__(self):
        return f"{self.name} (${self.price})"


class Reservation(models.Model):
    SEATING_CHOICES = [
        ('main', 'Main Dining Hall'),
        ('terrace', 'Skyline Panorama Terrace'),
        ('chef_counter', "Chef's Tasting Counter (Exclusive)"),
        ('private', 'Private Cellar Room'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    booking_code = models.CharField(max_length=12, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    guests = models.PositiveIntegerField(default=2)
    seating_area = models.CharField(max_length=30, choices=SEATING_CHOICES, default='main')
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = f"RES-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_code} - {self.customer_name} ({self.date} {self.time_slot})"


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('dine_in', 'Dine-In Table Service'),
        ('takeaway', 'Luxury Express Takeaway'),
        ('delivery', 'White-Glove Private Delivery'),
    ]

    STATUS_CHOICES = [
        ('received', 'Received'),
        ('preparing', 'In Kitchen Preparation'),
        ('ready', 'Ready for Service'),
        ('completed', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=16, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    table_or_address = models.CharField(max_length=255, blank=True, help_text="Table # or delivery address")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    tip_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='Credit Card')
    card_last4 = models.CharField(max_length=4, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (${self.total})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    item_subtotal = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.item_name} for {self.order.order_number}"


class Testimonial(models.Model):
    author_name = models.CharField(max_length=120)
    designation = models.CharField(max_length=120, default='Epicurean Connoisseur')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    dish_highlight = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"


class DishReview(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dish_reviews')
    author_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    headline = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.menu_item.update_rating()

    def __str__(self):
        return f"{self.rating}★ for {self.menu_item.name} by {self.author_name}"
