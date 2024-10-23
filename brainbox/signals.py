from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project
from .views import ProjectView

@receiver(post_save, sender=Project)
def project_save(sender, **kwargs):
    ProjectView().invalidate_cache()
