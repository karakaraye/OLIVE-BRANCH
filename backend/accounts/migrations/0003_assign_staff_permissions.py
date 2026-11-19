from django.db import migrations

ROLE_SCREENS = {
    "reception": "reception",
    "cashier": "outlet",
    "stores": "stock",
    "accountant": "reconciliation",
    "manager": "approvals",
    "owner": "reports",
    "admin": "accounts",
}


def assign_permissions(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    StaffProfile = apps.get_model("accounts", "StaffProfile")
    User = apps.get_model("auth", "User")
    Outlet = apps.get_model("outlets", "Outlet")
    content_type, _ = ContentType.objects.using(alias).get_or_create(
        app_label="accounts", model="staffaccess"
    )
    names = dict(apps.get_model("accounts", "StaffAccess")._meta.permissions)
    for role, screen in ROLE_SCREENS.items():
        group, _ = Group.objects.using(alias).get_or_create(name=role)
        codes = ["access_staff", f"access_{screen}_screen"]
        if role in ("accountant", "manager", "owner", "admin"):
            codes.append("view_foundation")
        if role == "admin":
            codes.append("search_audit")
        for code in codes:
            permission, _ = Permission.objects.using(alias).get_or_create(
                content_type=content_type, codename=code, defaults={"name": names[code]}
            )
            group.permissions.add(permission)

    cashier = (
        User.objects.using(alias)
        .filter(username="demo-cashier", groups__name="cashier")
        .first()
    )
    restaurant = Outlet.objects.using(alias).filter(name="Restaurant").first()
    if cashier and restaurant:
        StaffProfile.objects.using(alias).get_or_create(
            user=cashier, defaults={"outlet": restaurant}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_staffaccess_options_staffprofile"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [migrations.RunPython(assign_permissions, migrations.RunPython.noop)]
