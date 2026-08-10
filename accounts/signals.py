from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
)

from django.db.models.signals import (
    post_save,
)

from django.dispatch import receiver

from .models import User

from .services import (

    save_login_history,

    update_logout_history,

    log_login,

    log_logout,

    create_notification,

)

# ==========================================================
# USER LOGIN
# ==========================================================

@receiver(user_logged_in)
def user_login_signal(

    sender,

    request,

    user,

    **kwargs,

):

    save_login_history(

        request=request,

        user=user,

    )

    log_login(

        user=user,

        request=request,

    )

    # ==========================================================
# USER LOGOUT
# ==========================================================

@receiver(user_logged_out)
def user_logout_signal(

    sender,

    request,

    user,

    **kwargs,

):

    if user:

        update_logout_history(request)

        log_logout(

            user=user,

            request=request,

        )


        # ==========================================================
# WELCOME NOTIFICATION
# ==========================================================

@receiver(post_save, sender=User)
def create_welcome_notification(

    sender,

    instance,

    created,

    **kwargs,

):

    if created:

        create_notification(

            user=instance,

            title="Welcome",

            message=(
                "Welcome to Smart Campus Management System."
            ),

        )