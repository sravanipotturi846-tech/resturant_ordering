import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def clean_text_for_email(text):
    """Normalize unicode characters for cross-platform email & console backends."""
    if not text:
        return ''
    return text.replace('✦', '*').replace('★', '*').encode('ascii', 'replace').decode('ascii')


def send_reservation_confirmation_email(reservation):
    """Compile and dispatch high-end HTML booking confirmation email."""
    if not reservation.email:
        return False

    subject = f"[L'Etoile Doree] Table Reservation Confirmed #{reservation.booking_code}"
    
    context = {
        'reservation': reservation,
    }

    try:
        html_message = render_to_string('emails/reservation_confirmation.html', context)
        plain_message = clean_text_for_email(strip_tags(html_message))

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Reservation confirmation email dispatched to {reservation.email} for {reservation.booking_code}")
        return True
    except Exception as e:
        logger.error(f"Error dispatching reservation email: {e}")
        return False


def send_order_receipt_email(order):
    """Compile and dispatch high-end HTML tasting order receipt email."""
    if not order.email:
        return False

    subject = f"[L'Etoile Doree] Tasting Order Receipt #{order.order_number}"

    context = {
        'order': order,
    }

    try:
        html_message = render_to_string('emails/order_receipt.html', context)
        plain_message = clean_text_for_email(strip_tags(html_message))

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Order receipt email dispatched to {order.email} for {order.order_number}")
        return True
    except Exception as e:
        logger.error(f"Error dispatching order receipt email: {e}")
        return False
