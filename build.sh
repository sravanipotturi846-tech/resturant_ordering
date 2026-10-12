#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing Python production dependencies..."
pip install -r requirements.txt

echo "==> Collecting static assets via WhiteNoise..."
python manage.py collectstatic --no-input --clear

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Seeding luxury restaurant dishes and menu..."
python manage.py populate_restaurant

echo "==> Ensuring admin superuser exists..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@letoiledoree.com', 'adminpassword123')"

echo "==> Build finished successfully!"


