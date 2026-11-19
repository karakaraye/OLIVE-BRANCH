from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.models import Group
from django.db import connection, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from accounts.forms import (
    AccountChangeForm,
    AccountCreateForm,
    AccountRoleForm,
    StaffAuthenticationForm,
)
from accounts.models import StaffProfile
from accounts.roles import ROLE_SCREENS, screen_permission
from accounts.sessions import client_request_id
from audit.models import AuditEvent
from outlets.models import Outlet

User = get_user_model()


def error(message, status):
    return JsonResponse({"error": message}, status=status)


def permission_error(request, permission):
    if not request.user.is_authenticated:
        return error("Sign in to continue.", 401)
    if not request.user.has_perm(f"accounts.{permission}"):
        return error("You do not have permission to open this screen.", 403)
    return None


def roles_for(user):
    return [group.name for group in user.groups.all() if group.name in ROLE_SCREENS]


@never_cache
@require_GET
def session(request):
    csrf_token = get_token(request)
    denied = permission_error(request, "access_staff")
    if denied:
        data = {"csrfToken": csrf_token, "staff": None}
    else:
        data = {
            "csrfToken": csrf_token,
            "staff": {
                "username": request.user.get_username(),
                "roles": roles_for(request.user),
            },
            "screens": [
                {
                    "slug": screen,
                    "title": title,
                    "allowed": request.user.has_perm(
                        f"accounts.{screen_permission(screen)}"
                    ),
                }
                for screen, title, _ in ROLE_SCREENS.values()
            ],
            "canSearchAudit": request.user.has_perm("accounts.search_audit"),
        }
    return JsonResponse(data)


@never_cache
@require_POST
def sign_in(request):
    if not client_request_id(request):
        return error("Provide a UUID Idempotency-Key.", 400)
    form = StaffAuthenticationForm(request, data=request.POST)
    if not form.is_valid():
        if not request.POST.get("username") or not request.POST.get("password"):
            return error("Enter your username and password.", 400)
        return error("The username or password was rejected.", 401)
    login(request, form.get_user())
    return JsonResponse({"signedIn": True})


@never_cache
@require_POST
def sign_out(request):
    if not client_request_id(request):
        return error("Provide a UUID Idempotency-Key.", 400)
    logout(request)
    return JsonResponse({"signedIn": False})


@never_cache
@require_GET
def screen(request, slug):
    areas = {
        screen: (title, description)
        for screen, title, description in ROLE_SCREENS.values()
    }
    if slug not in areas:
        return error("Screen not found.", 404)
    denied = permission_error(request, screen_permission(slug))
    if denied:
        return denied
    title, description = areas[slug]
    data = {"title": title, "description": description}
    if slug == "outlet":
        outlet = Outlet.objects.filter(staffprofile__user=request.user).values_list(
            "name", flat=True
        )
        data["outlet"] = outlet.first()
    return JsonResponse(data)


def account_data(user):
    profile = getattr(user, "staffprofile", None)
    return {
        "id": user.pk,
        "username": user.username,
        "name": user.get_full_name(),
        "roles": roles_for(user),
        "active": user.is_active,
        "outlet": profile.outlet_id if profile else None,
    }


@never_cache
@require_http_methods(["GET", "POST"])
def accounts(request):
    denied = permission_error(request, screen_permission("accounts"))
    if denied:
        return denied
    if request.method == "POST":
        return change_account(request, "create")
    users = User.objects.filter(groups__name__in=ROLE_SCREENS).distinct()
    users = (
        users.select_related("staffprofile")
        .prefetch_related("groups")
        .order_by("username")
    )
    return JsonResponse(
        {
            "accounts": [account_data(user) for user in users],
            "outlets": list(Outlet.objects.order_by("name").values("id", "name")),
            "roles": list(ROLE_SCREENS),
        }
    )


@never_cache
@require_POST
def update_account(request, user_id, operation):
    denied = permission_error(request, screen_permission("accounts"))
    if denied:
        return denied
    if user_id == request.user.pk:
        return error("Ask another administrator to change your account.", 409)
    return change_account(request, operation, user_id)


@transaction.atomic
def change_account(request, operation, user_id=None):
    forms = {
        "create": AccountCreateForm,
        "role": AccountRoleForm,
        "disable": AccountChangeForm,
        "enable": AccountChangeForm,
    }
    actions = {
        "create": AuditEvent.Action.ACCOUNT_CREATED,
        "role": AuditEvent.Action.ROLE_CHANGED,
        "disable": AuditEvent.Action.ACCOUNT_DISABLED,
        "enable": AuditEvent.Action.ACCOUNT_ENABLED,
    }
    if operation not in forms or (operation == "create") != (user_id is None):
        return error("Operation not found.", 404)
    request_id = client_request_id(request)
    if not request_id:
        return error("Provide a UUID Idempotency-Key.", 400)
    form = forms[operation](request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    data = form.cleaned_data
    action = actions[operation]
    details = {}
    if operation == "create":
        details.update(
            {field: data[field] for field in ("username", "first_name", "last_name")}
        )
    if operation in ("create", "role"):
        details.update(
            role=data["role"], outlet=data["outlet"].pk if data["outlet"] else None
        )

    # Serialize access changes and retries so their account and audit writes commit together.
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s, %s)", [81231, 2])

    existing = AuditEvent.objects.filter(request_id=request_id).first()
    if existing:
        matches = (
            existing.actor_id == request.user.pk
            and existing.action == action
            and existing.reason == data["reason"]
            and all(
                existing.details.get(key) == value for key, value in details.items()
            )
            and (user_id is None or existing.affected_record == f"staff:{user_id}")
        )
        if not matches:
            return error("This request ID was already used for another operation.", 409)
        return JsonResponse(
            {"record": existing.affected_record}, status=201 if user_id is None else 200
        )

    if user_id is None:
        if User.objects.filter(username=data["username"]).exists():
            return error("That username already exists.", 409)
        user = User.objects.create_user(
            **{
                field: data[field]
                for field in ("username", "first_name", "last_name", "password")
            }
        )
    else:
        user = (
            User.objects.select_for_update()
            .filter(pk=user_id, is_superuser=False)
            .first()
        )
        if user is not None and not roles_for(user):
            user = None
        if user is None:
            return error("Staff account not found.", 404)

    profile, _ = StaffProfile.objects.get_or_create(user=user)
    if operation in ("create", "role"):
        if operation == "role":
            details.update(
                previous_roles=roles_for(user), previous_outlet=profile.outlet_id
            )
        user.groups.set([Group.objects.get(name=data["role"])])
        user.user_permissions.clear()
        profile.outlet = data["outlet"]
        profile.save(update_fields=["outlet"])
    else:
        active = operation == "enable"
        if user.is_active == active:
            return error("The account is already in that state.", 409)
        user.is_active = active
        user.save(update_fields=["is_active"])
        if not active:
            profile.session_version += 1
            profile.save(update_fields=["session_version"])

    record = f"staff:{user.pk}"
    AuditEvent.objects.create(
        request_id=request_id,
        actor=request.user,
        actor_label=request.user.get_username(),
        action=action,
        affected_record=record,
        reason=data["reason"],
        details=details,
    )
    return JsonResponse({"record": record}, status=201 if user_id is None else 200)
