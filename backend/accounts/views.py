from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from outlets.models import Outlet
from rooms.models import Room


@login_required
@permission_required("accounts.access_staff", raise_exception=True)
def staff_home(request):
    return render(request, "accounts/home.html")


@login_required
@permission_required("accounts.view_foundation", raise_exception=True)
def foundation(request):
    return render(request, "accounts/foundation.html", foundation_counts())


def foundation_counts():
    return {"rooms": Room.objects.count(), "outlets": Outlet.objects.count()}


class CanViewFoundation(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("accounts.view_foundation")


@api_view(["GET"])
@permission_classes([CanViewFoundation])
def foundation_api(request):
    return Response(foundation_counts())
