"""
Management command to create a default admin user
Usage: python manage.py create_default_admin
"""
from django.core.management.base import BaseCommand
from accounts.models import User, UserRole


class Command(BaseCommand):
    help = 'Creates a default admin user for VPulse'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@vpulse.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            name='Admin User',
            role=UserRole.ADMIN,
            balance=10000.00
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user!\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'\nPlease change the password after first login!'
            )
        )

