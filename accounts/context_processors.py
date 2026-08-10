from django.db.models import Q
from announcements.models import Announcement


def global_data(request):

    context = {}

    if request.user.is_authenticated:

        announcements = Announcement.objects.filter(

            Q(target="ALL") |

            Q(target=request.user.role)

        ).order_by("-created_at")[:5]

        context["notifications"] = announcements

        context["notifications_count"] = announcements.count()

    else:

        context["notifications"] = []

        context["notifications_count"] = 0

    return context