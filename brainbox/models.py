from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Project(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(unique=True, max_length=200)
    project_content = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f"{self.project_name} by {self.owner.name}"

