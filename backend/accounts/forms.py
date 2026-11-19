from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.signals import user_login_failed

from accounts.roles import ROLE_SCREENS
from outlets.models import Outlet


class StaffAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.has_perm("accounts.access_staff"):
            user_login_failed.send(
                sender=__name__,
                credentials={"username": user.get_username()},
                request=self.request,
            )
            raise self.get_invalid_login_error()


class AccountChangeForm(forms.Form):
    reason = forms.CharField(max_length=255)


class AccountRoleForm(AccountChangeForm):
    role = forms.ChoiceField(choices=[(role, role) for role in ROLE_SCREENS])
    outlet = forms.ModelChoiceField(
        queryset=Outlet.objects.order_by("name"), required=False
    )

    def clean(self):
        data = super().clean()
        if data.get("role") and (data["role"] == "cashier") != (
            data.get("outlet") is not None
        ):
            self.add_error("outlet", "Select an outlet for cashier accounts only.")
        return data


class AccountCreateForm(AccountRoleForm):
    username = forms.CharField(
        max_length=150, validators=[get_user_model().username_validator]
    )
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(max_length=256, strip=False)

    def clean(self):
        data = super().clean()
        if data.get("password"):
            user = get_user_model()(
                **{
                    field: data.get(field, "")
                    for field in ("username", "first_name", "last_name")
                }
            )
            try:
                validate_password(data["password"], user)
            except forms.ValidationError as exc:
                self.add_error("password", exc)
        return data
