# Generated by Django 3.1.5 on 2021-02-02 17:28

from django.db import migrations, models
import django.db.models.deletion
import lessons.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0005_coursesignup'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseLesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
                ('course_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.coursesection')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_lessons.baselesson_set+', to='contenttypes.contenttype')),
            ],
            options={
                'order_with_respect_to': 'course_section',
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('baselesson_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lessons.baselesson')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lessons.baselesson',),
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('baselesson_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lessons.baselesson')),
                ('video', models.FileField(blank=True, null=True, upload_to=lessons.models.get_lesson_video_upload_directory)),
                ('additional_materials', models.FileField(blank=True, null=True, upload_to=lessons.models.get_lesson_additional_materials_upload_directory)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lessons.baselesson',),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('baselesson_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lessons.baselesson')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lessons.baselesson',),
        ),
    ]