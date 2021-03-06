from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    Model,
    TextField,
)
from django.db.models.signals import post_save

import courses.signals
from courses.querysets import CourseQuerySet


def get_course_upload_directory(course: "Course", filename: str) -> str:
    return f"images/courses/{course.id}/{filename}"


class Course(Model):
    name = CharField(max_length=64)
    description = TextField()
    cover_image = ImageField(upload_to=get_course_upload_directory)
    small_cover_image = ImageField(null=True, blank=True, upload_to=get_course_upload_directory)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} ({self.id})"


class CourseSection(Model):
    course = ForeignKey(Course, on_delete=CASCADE, related_name="course_sections")
    name = CharField(max_length=64)

    class Meta:
        order_with_respect_to = "course"

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.course}"


class CourseSignup(Model):
    course = ForeignKey(Course, related_name="signups", on_delete=CASCADE)
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name="signups", on_delete=CASCADE)

    class Meta:
        unique_together = ("course", "user")


post_save.connect(courses.signals.cover_image_resize_callback, sender=Course)
