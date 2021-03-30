from django.contrib.admin import ModelAdmin, TabularInline, site

from lessons.models import Answer, Exercise, Lesson, Test, TestQuestion


class BaseLessonAdmin(ModelAdmin):
    list_display = ("name", "course_section")


class AnswerInline(TabularInline):
    model = Answer
    extra = 2


class QuestionAdmin(ModelAdmin):
    inlines = [AnswerInline]


site.register(Lesson, BaseLessonAdmin)
site.register(Exercise, BaseLessonAdmin)
site.register(Test, BaseLessonAdmin)
site.register(TestQuestion, QuestionAdmin)
