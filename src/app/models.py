from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=100, blank=False)
    alphanumeric_code = models.CharField(max_length=10, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(max_length=1000, blank=False, default=False)
    questions = models.JSONField() # List of jsons with keys 'question', 'is_multiple_answers' and 'answers', that is a list of jsons with keys 'answer' and 'is_correct'

    def __str__(self):
        return f"{self.title}: {self.alphanumeric_code}"

    class Meta:
        ordering = ["-id"]