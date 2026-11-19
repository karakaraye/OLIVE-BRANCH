from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.management.commands.seed_demo import DEMO_PASSWORD
from audit.models import AuditEvent
from outlets.models import Outlet
from rooms.models import Room, RoomType


class FoundationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", request_id="foundation-test", stdout=StringIO())

    def test_seed_is_repeatable_and_creates_expected_fixtures(self):
        call_command("seed_demo", request_id="foundation-test", stdout=StringIO())
        for name, count in (("Standard", 10), ("Deluxe", 6), ("Suite", 4)):
            self.assertEqual(Room.objects.filter(room_type__name=name).count(), count)
        self.assertEqual(RoomType.objects.count(), 3)
        self.assertEqual(Room.objects.count(), 20)
        self.assertCountEqual(
            Outlet.objects.values_list("name", flat=True), ["Restaurant", "Pool Bar"]
        )
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 7)
        for role in (
            "reception",
            "cashier",
            "stores",
            "accountant",
            "manager",
            "owner",
            "admin",
        ):
            user = users.get(username=f"demo-{role}")
            self.assertEqual(list(user.groups.values_list("name", flat=True)), [role])
            self.assertTrue(user.check_password(DEMO_PASSWORD))
        event = AuditEvent.objects.get()
        self.assertEqual(event.actor.username, "demo-admin")
        self.assertTrue(timezone.is_aware(event.occurred_at))
        self.assertTrue(event.reason)
        self.assertEqual(event.affected_record, "demo-fixtures:v1")

    @override_settings(ALLOW_DEMO_SEED=False)
    def test_seed_is_disabled_outside_development_and_test(self):
        with self.assertRaisesMessage(CommandError, "only in development and test"):
            call_command("seed_demo", request_id="disabled-test", stdout=StringIO())

    def test_audit_events_reject_update_delete_and_truncate(self):
        for action in (
            lambda: AuditEvent.objects.update(reason="changed"),
            lambda: AuditEvent.objects.all().delete(),
            self.truncate_events,
        ):
            with (
                self.subTest(action=action),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                action()
        self.assertEqual(AuditEvent.objects.count(), 1)

    @staticmethod
    def truncate_events():
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute("TRUNCATE audit_auditevent")

    def test_staff_can_sign_in_but_cannot_open_unpermitted_views(self):
        home = reverse("staff-home")
        login = reverse("staff-login")
        self.assertRedirects(self.client.get(home), f"{login}?next={home}")
        self.assertEqual(self.client.get(reverse("foundation-api")).status_code, 403)
        self.assertRedirects(
            self.client.post(
                login, {"username": "demo-reception", "password": DEMO_PASSWORD}
            ),
            home,
        )
        self.assertContains(self.client.get(home), "Signed in as demo-reception.")
        self.assertEqual(self.client.get(reverse("staff-foundation")).status_code, 403)
        self.assertEqual(self.client.get(reverse("foundation-api")).status_code, 403)
        self.assertRedirects(self.client.post(reverse("staff-logout")), login)

    def test_manager_can_open_foundation_screen_and_api(self):
        self.assertTrue(
            self.client.login(username="demo-manager", password=DEMO_PASSWORD)
        )
        self.assertContains(
            self.client.get(reverse("staff-foundation")), "<dd>20</dd>", html=True
        )
        self.assertEqual(
            self.client.get(reverse("foundation-api")).json(),
            {"rooms": 20, "outlets": 2},
        )
