from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates default admin and user accounts with registered full names.'

    def handle(self, *args, **options):
        # Create/Update Admin Account
        admin_user, created = User.objects.get_or_create(username='admin')
        admin_user.email = 'admin@thaagam.org'
        admin_user.first_name = 'Priya Sharma'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Admin account ready: admin (Priya Sharma) / admin123"))

        # Create/Update Regular User Account
        normal_user, created = User.objects.get_or_create(username='user1')
        normal_user.email = 'user1@example.com'
        normal_user.first_name = 'Arun Kumar'
        normal_user.is_staff = False
        normal_user.is_superuser = False
        normal_user.set_password('user123')
        normal_user.save()
        self.stdout.write(self.style.SUCCESS("User account ready: user1 (Arun Kumar) / user123"))
