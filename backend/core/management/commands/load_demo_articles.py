from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Article


class Command(BaseCommand):
    help = "Load sample articles into the database (default: 150). Idempotent."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=150,
            help="Number of sample articles to ensure exist (default: 150)",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="demo_user",
            help="Username to use as 'created_by'. If missing, it will be created.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        username = options["username"]

        User = get_user_model()
        user, created_user = User.objects.get_or_create(username=username)
        # If we had to create the user and it's the default demo user, set a known password
        if created_user and username == "demo_user":
            user.set_password("demo_user_1234")
            user.save(update_fields=["password"])

        identifiers = [f"ART-{i:06d}" for i in range(1, count + 1)]

        existing = set(
            Article.objects.filter(identifier__in=identifiers).values_list(
                "identifier", flat=True
            )
        )

        base_date = date.today()
        to_create = []
        for ident in identifiers:
            if ident in existing:
                continue

            # derive a stable number from identifier
            try:
                i = int(ident.split("-")[1])
            except (IndexError, ValueError):
                i = 1

            pub_date = base_date - timedelta(days=(i % 365))
            title = f"Sample Article {i:03d}"
            abstract = (
                f"This is a sample abstract for article number {i:03d}. "
                "It contains placeholder content for testing the API and database. "
                "Repeated text helps simulate realistic abstract length."
            )

            to_create.append(
                Article(
                    identifier=ident,
                    publication_date=pub_date,
                    title=title,
                    abstract=abstract,
                    created_by=user,
                )
            )

        created_count = 0
        if to_create:
            with transaction.atomic():
                Article.objects.bulk_create(to_create, batch_size=500)
            created_count = len(to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Ensured {count} sample articles exist. Created {created_count}, {len(existing)} already present."
            )
        )
