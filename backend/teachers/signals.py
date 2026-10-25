from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import TeacherProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):

    if created and instance.role == "TEACHER":

        TeacherProfile.objects.get_or_create(
            user=instance,
            defaults={
                "employee_id": f"T{instance.id:04d}",
                "status": "ACTIVE",
            },
        )


@receiver(post_save, sender=User)
def save_teacher_profile(sender, instance, **kwargs):

    if instance.role == "TEACHER":

        if hasattr(instance, "teacher_profile"):
            instance.teacher_profile.save()