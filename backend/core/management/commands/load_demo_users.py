from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create demo users"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users_to_create = [
            ("demo_user1", "demo_user1_1234"),
            ("demo_user2", "demo_user2_1234"),
        ]

        for username, password in users_to_create:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password)
                self.stdout.write(
                    self.style.SUCCESS(f"Created demo user {username}/{password}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Demo user '{username}' already exists")
                )