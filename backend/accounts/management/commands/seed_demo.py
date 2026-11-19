from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from accounts.models import StaffProfile
from accounts.roles import ROLE_SCREENS
from audit.models import AuditEvent
from outlets.models import Outlet
from rooms.models import Room, RoomType

ROLES = tuple(ROLE_SCREENS)
ROOM_TYPES = (("Standard", 10), ("Deluxe", 6), ("Suite", 4))
DEMO_PASSWORD = "olive-demo-local-only"
AFFECTED_RECORD = "demo-fixtures:v1"


class Command(BaseCommand):
    help = "Create the fictional hotel fixtures in development or test."

    def add_arguments(self, parser):
        parser.add_argument("--request-id", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        if not getattr(settings, "ALLOW_DEMO_SEED", False):
            raise CommandError(
                "Demo seeding is available only in development and test."
            )

        request_id = options["request_id"].strip()
        if not request_id or len(request_id) > 100:
            raise CommandError("Provide a request ID containing 1 to 100 characters.")

        with connection.cursor() as cursor:
            # Serialize seed invocations, including those with different request IDs.
            cursor.execute("SELECT pg_advisory_xact_lock(%s, %s)", [81231, 1])

        existing = AuditEvent.objects.filter(request_id=request_id).first()
        if existing:
            if existing.affected_record != AFFECTED_RECORD:
                raise CommandError("This request ID belongs to another operation.")
            self.stdout.write("Demo fixtures already seeded for this request.")
            return

        user_model = get_user_model()
        if user_model.objects.filter(
            username__in=[f"demo-{role}" for role in ROLES]
        ).exists():
            raise CommandError(
                "Demo usernames already exist. Reuse the original seed request ID."
            )

        users = {}
        for role in ROLES:
            group = Group.objects.get(name=role)
            user = user_model.objects.create_user(
                username=f"demo-{role}", password=DEMO_PASSWORD
            )
            user.groups.add(group)
            users[role] = user

        number = 101
        for name, count in ROOM_TYPES:
            room_type, _ = RoomType.objects.get_or_create(name=name)
            for _ in range(count):
                Room.objects.get_or_create(
                    number=str(number), defaults={"room_type": room_type}
                )
                number += 1

        for name in ("Restaurant", "Pool Bar"):
            Outlet.objects.get_or_create(name=name)

        StaffProfile.objects.create(
            user=users["cashier"], outlet=Outlet.objects.get(name="Restaurant")
        )

        AuditEvent.objects.create(
            request_id=request_id,
            actor=users["admin"],
            reason="Initialize fictional hotel data from the local management command",
            affected_record=AFFECTED_RECORD,
        )
        self.stdout.write(
            self.style.SUCCESS("Seeded 20 rooms, 2 outlets and 7 demo users.")
        )
