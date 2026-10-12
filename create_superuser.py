import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from restaurant.models import MenuItem

# 1. Ensure Menu & Restaurant Data are Populated
if not MenuItem.objects.exists():
    print("==> No dishes found in database. Seeding luxury restaurant menu & categories...")
    call_command('populate_restaurant')
else:
    print(f"==> Menu already populated ({MenuItem.objects.count()} dishes ready).")

# 2. Ensure Superuser Exists
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@letoiledoree.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"==> Superuser '{username}' created successfully.")
else:
    print(f"==> Superuser '{username}' already exists.")
