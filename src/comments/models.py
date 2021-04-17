from django.conf import settings
from django.db.models import CASCADE, SET_NULL, CharField, DateTimeField, ForeignKey, Model

from lessons.models import Lesson


class Comment(Model):
    author = ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=SET_NULL, related_name="comments", null=True
    )
    lesson = ForeignKey(Lesson, related_name="comments", on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True, db_index=True)
    text = CharField(max_length=1024)

    class Meta:
        ordering = ["-created"]
