from datetime import UTC, date, datetime, time, timedelta

from django.db.models import Q
from django.http import JsonResponse
from django.utils.timezone import get_current_timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from accounts.api import error, permission_error
from audit.models import AuditEvent

PAGE_SIZE = 50


@never_cache
@require_GET
def search(request):
    denied = permission_error(request, "search_audit")
    if denied:
        return denied

    events = AuditEvent.objects.select_related("actor").order_by("-occurred_at", "-pk")
    actor = request.GET.get("actor", "").strip()
    record = request.GET.get("record", "").strip()
    day = request.GET.get("date", "").strip()
    if actor:
        events = events.filter(
            Q(actor_label__icontains=actor)
            | Q(actor_label="", actor__username__icontains=actor)
        )
    if record:
        events = events.filter(affected_record__icontains=record)
    try:
        page = int(request.GET.get("page", "1"))
        if not 1 <= page <= 10000:
            raise ValueError
        if day:
            start = datetime.combine(
                date.fromisoformat(day), time.min, get_current_timezone()
            )
            events = events.filter(
                occurred_at__gte=start, occurred_at__lt=start + timedelta(days=1)
            )
    except (ValueError, OverflowError):
        return error("Use a valid page and date (YYYY-MM-DD).", 400)

    offset = (page - 1) * PAGE_SIZE
    rows = list(events[offset : offset + PAGE_SIZE + 1])
    return JsonResponse(
        {
            "hasMore": len(rows) > PAGE_SIZE,
            "events": [
                {
                    "id": event.pk,
                    "action": event.get_action_display(),
                    "actor": event.actor_label
                    or (event.actor.get_username() if event.actor else ""),
                    "actorVerified": event.actor_id is not None,
                    "time": event.occurred_at.astimezone(UTC).isoformat(),
                    "reason": event.reason,
                    "record": event.affected_record,
                }
                for event in rows[:PAGE_SIZE]
            ],
        }
    )
