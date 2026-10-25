import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .services.ai_service import CampusAIService

@login_required
def chat_page(request):
    user_role = getattr(request.user, "role", "USER")
    full_name = request.user.get_full_name() or request.user.username
    context = {
        "title": "Campus AI Assistant",
        "user_role": user_role,
        "user_name": full_name,
    }
    return render(request, "ai/chat.html", context)

@login_required
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
        history = data.get("history", [])
        confirm_action_id = data.get("confirm_action_id")
        clear_context = data.get("clear_context", False)
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid request format.", "ui_action": None}, status=400)

    # Session-isolated context store
    if "ai_context" not in request.session:
        request.session["ai_context"] = {}

    session_context = request.session["ai_context"]

    user_role = getattr(request.user, "role", "USER")

    ai_response = CampusAIService.generate_response(
        user_message=user_message,
        user=request.user,
        session_context=session_context,
        history=history,
        confirm_action_id=confirm_action_id,
        clear_context=clear_context
    )

    # Save updated session context
    request.session["ai_context"] = session_context
    request.session.modified = True

    return JsonResponse({
        "success": ai_response.get("success", True),
        "message": ai_response.get("message", ""),
        "ui_action": ai_response.get("ui_action", None),
        "confirmation_required": ai_response.get("confirmation_required", False),
        "pending_action_id": ai_response.get("pending_action_id", None),
        "confirmation_preview": ai_response.get("confirmation_preview", None),
        "active_context": ai_response.get("active_context", None),
        "role": user_role
    })
