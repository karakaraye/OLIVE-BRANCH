from io import StringIO
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.utils import timezone

from accounts.management.commands.seed_demo import DEMO_PASSWORD
from accounts.roles import ROLE_SCREENS
from accounts.sessions import SESSION_STARTED
from audit.models import AuditEvent
from outlets.models import Outlet

BASE = "/api/staff/"
User = get_user_model()


class StaffAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", request_id="staff-tests", stdout=StringIO())

    def post(self, client, path, data=None, key=None):
        csrf = client.get(BASE + "session/").json()["csrfToken"]
        return client.post(
            BASE + path,
            data or {},
            headers={"X-CSRFToken": csrf, "Idempotency-Key": str(key or uuid4())},
        )

    def sign_in(self, role):
        client = Client(enforce_csrf_checks=True)
        response = self.post(
            client, "login/", {"username": f"demo-{role}", "password": DEMO_PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        return client

    def test_each_role_can_open_its_screen_and_receives_a_real_denial(self):
        for role, (screen, _, _) in ROLE_SCREENS.items():
            with self.subTest(role=role):
                client = self.sign_in(role)
                blocked = "outlet" if role == "reception" else "reception"
                self.assertEqual(
                    client.get(BASE + f"screens/{screen}/").status_code, 200
                )
                self.assertEqual(
                    client.get(BASE + f"screens/{blocked}/").status_code, 403
                )
                advertised = {
                    row["slug"]: row["allowed"]
                    for row in client.get(BASE + "session/").json()["screens"]
                }
                self.assertTrue(advertised[screen])
                self.assertFalse(advertised[blocked])
        cashier = self.sign_in("cashier")
        self.assertEqual(
            cashier.get(BASE + "screens/outlet/").json()["outlet"], "Restaurant"
        )
        self.assertEqual(cashier.get(BASE + "accounts/").status_code, 403)
        self.assertEqual(cashier.get(BASE + "audit/").status_code, 403)

    def test_disabling_blocks_active_and_old_sessions_and_audits_enable(self):
        admin = self.sign_in("admin")
        client = self.sign_in("reception")
        user = User.objects.get(username="demo-reception")
        disable = f"accounts/{user.pk}/disable/"
        key = uuid4()
        self.assertEqual(
            self.post(admin, disable, {"reason": "Staff departed"}, key).status_code,
            200,
        )
        self.assertEqual(
            self.post(admin, disable, {"reason": "Staff departed"}, key).status_code,
            200,
        )
        self.assertEqual(client.get(BASE + "screens/reception/").status_code, 401)
        self.assertEqual(
            self.post(
                client, "login/", {"username": user.username, "password": DEMO_PASSWORD}
            ).status_code,
            401,
        )
        enabled = self.post(
            admin, f"accounts/{user.pk}/enable/", {"reason": "Staff returned"}
        )
        self.assertEqual(enabled.status_code, 200)
        self.assertEqual(client.get(BASE + "screens/reception/").status_code, 401)
        self.sign_in("reception")
        events = AuditEvent.objects.filter(
            affected_record=f"staff:{user.pk}",
            action__in=["account_enabled", "account_disabled"],
        )
        self.assertCountEqual(
            events.values_list("action", flat=True),
            ["account_enabled", "account_disabled"],
        )
        self.assertEqual(
            set(events.values_list("actor__username", flat=True)), {"demo-admin"}
        )

    def test_login_logout_failure_and_timeout_are_audited(self):
        client = Client(enforce_csrf_checks=True)
        credentials = {"username": "demo-cashier", "password": "wrong-password"}
        key = uuid4()
        self.assertEqual(self.post(client, "login/", credentials, key).status_code, 401)
        self.assertEqual(self.post(client, "login/", credentials, key).status_code, 401)
        self.assertEqual(client.post(BASE + "login/", credentials).status_code, 403)
        failed = AuditEvent.objects.get(action="login_failed")
        self.assertIsNone(failed.actor_id)
        self.assertEqual(failed.actor_label, "demo-cashier")
        self.assertNotIn("wrong-password", str(failed.details))

        client = self.sign_in("cashier")
        self.assertEqual(self.post(client, "logout/").status_code, 200)
        self.assertIsNone(client.get(BASE + "session/").json()["staff"])

        client = self.sign_in("cashier")
        session = client.session
        session[SESSION_STARTED] = (
            int(timezone.now().timestamp()) - settings.SESSION_COOKIE_AGE
        )
        session.save()
        self.assertEqual(client.get(BASE + "screens/outlet/").status_code, 401)
        self.assertCountEqual(
            AuditEvent.objects.filter(actor__username="demo-cashier")
            .exclude(action="seed")
            .values_list("action", flat=True),
            ["login", "logout", "login", "logout"],
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                action="logout", reason="Staff session expired"
            ).exists()
        )

    def test_named_account_creation_and_permission_change_are_audited_and_searchable(
        self,
    ):
        admin = self.sign_in("admin")
        pool_bar = Outlet.objects.get(name="Pool Bar")
        staff = {
            "username": "staff-akpan",
            "first_name": "Ini",
            "last_name": "Akpan",
            "password": "River-lantern-583!",
            "role": "cashier",
            "outlet": pool_bar.pk,
            "reason": "New staff member",
        }
        key = uuid4()
        response = self.post(admin, "accounts/", staff, key)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.post(admin, "accounts/", staff, key).status_code, 201)
        self.assertEqual(
            self.post(
                admin, "accounts/", {**staff, "last_name": "Other"}, key
            ).status_code,
            409,
        )
        user = User.objects.get(username="staff-akpan")
        self.assertEqual(user.get_full_name(), "Ini Akpan")
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(self.post(client, "login/", staff).status_code, 200)
        self.assertEqual(
            client.get(BASE + "screens/outlet/").json()["outlet"], "Pool Bar"
        )
        change = f"accounts/{user.pk}/role/"
        self.assertEqual(
            self.post(admin, change, {"role": "reception"}).status_code, 400
        )
        self.assertEqual(
            self.post(
                admin, change, {"role": "reception", "reason": "Desk assignment"}
            ).status_code,
            200,
        )
        self.assertEqual(client.get(BASE + "screens/outlet/").status_code, 403)
        self.assertEqual(client.get(BASE + "screens/reception/").status_code, 200)

        event = AuditEvent.objects.get(action="role_changed")
        response = admin.get(
            BASE + "audit/",
            {
                "actor": "demo-admin",
                "record": f"staff:{user.pk}",
                "date": timezone.localtime(event.occurred_at).date().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            [row["action"] for row in response.json()["events"]],
            ["Account created", "Role changed"],
        )
        self.assertEqual(
            admin.get(BASE + "audit/", {"date": "invalid"}).status_code, 400
        )
        self.assertEqual(self.post(admin, "audit/").status_code, 405)
