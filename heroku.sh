#!/usr/bin/env bash
# Change this when it will come for real production
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell
python manage.py makemigrations telegramBot
python manage.py migrate