from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseSection, CourseSignup
from courses.signals import cover_image_resize_callback
from lessons.models import Lesson


class CoursesApiBaseTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(name="Test Course")
        self.list_url = reverse("courses:course-list")
        self.reorder_url_name = "courses:course-reorder-sections"
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="test"
        )
        # Disable signals
        signals.post_save.disconnect(cover_image_resize_callback, sender=Course)

    def tearDown(self):
        self.course.cover_image.delete(save=True)
        signals.post_save.connect(cover_image_resize_callback, sender=Course)

    def _add_course_permissions_to_user(self):
        permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Course)
        )
        self.user.user_permissions.set(permissions)


class CoursesApiAccessTestCase(CoursesApiBaseTestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("courses:course-list")

    def test_list_unauthenticated(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_authenticated_without_permissions(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, data={"name": "test course"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_authenticated_with_permissions(self):
        permission = Permission.objects.get(
            codename="add_course", content_type=ContentType.objects.get_for_model(Course)
        )
        self.user.user_permissions.add(permission)
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, data={"name": "test course"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_by_superuser(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, data={"name": "test course"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reorder_sections_access_by_unauthenticated(self):
        url = reverse(self.reorder_url_name, args=(self.course.id,))
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reorder_sections_access_without_permissions(self):
        self.client.force_authenticate(self.user)
        url = reverse(self.reorder_url_name, args=(self.course.id,))
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reorder_sections_with_permissions(self):
        self.client.force_authenticate(self.user)
        self._add_course_permissions_to_user()
        url = reverse(self.reorder_url_name, args=(self.course.id,))
        response = self.client.patch(url, data={"sections": []})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reorder_sections_with_invalid_method(self):
        self.client.force_authenticate(self.user)
        self._add_course_permissions_to_user()
        url = reverse(self.reorder_url_name, args=(self.course.id,))
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_assigned_lists_only_own(self):
        other_course = Course.objects.create(name="Test Course")
        CourseSignup.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(self.user)

        response = self.client.get(reverse("courses:course-list-assigned"))

        ids = [course["id"] for course in response.json()["results"]]
        self.assertIn(self.course.id, ids)
        self.assertNotIn(other_course.id, ids)

    def test_retrieve_assigned_lists_only_own(self):
        other_course = Course.objects.create(name="Test Course")
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("courses:course-retrieve-assigned", args=(other_course.id,))
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CourseApiTestCase(CoursesApiBaseTestCase):
    def setUp(self):
        super().setUp()
        self.reorder_url = reverse(self.reorder_url_name, args=(self.course.id,))
        self._add_course_permissions_to_user()
        self.client.force_authenticate(self.user)

    def test_reorder(self):
        section1 = CourseSection.objects.create(course=self.course)
        section2 = CourseSection.objects.create(course=self.course)
        data = {"sections": [section2.id, section1.id]}

        self.assertEqual(
            list(self.course.get_coursesection_order().values_list("id", flat=True)),
            [section1.id, section2.id],
        )
        self.client.patch(self.reorder_url, data=data)

        self.course.refresh_from_db()
        self.assertEqual(
            list(self.course.get_coursesection_order().values_list("id", flat=True)),
            [section2.id, section1.id],
        )

    def test_retrieve_assigned_structure(self):
        course_section = CourseSection.objects.create(course=self.course, name="test section")
        lesson = Lesson.objects.create(course_section=course_section, name="test_lesson")
        CourseSignup.objects.create(user=self.user, course=self.course)
        expected_data = {
            "id": self.course.id,
            "name": self.course.name,
            "sections": [
                {
                    "id": course_section.id,
                    "name": course_section.name,
                    "lessons": [
                        {
                            "id": lesson.id,
                            "name": lesson.name,
                            "isComplete": lesson.is_completed_by(self.user),
                        }
                    ],
                }
            ],
        }
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("courses:course-retrieve-assigned", args=(self.course.id,))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), expected_data)

    def test_retrieve_assigned_number_of_queries(self):
        course_section = CourseSection.objects.create(course=self.course, name="test section")
        Lesson.objects.create(course_section=course_section, name="test_lesson")
        CourseSignup.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(self.user)

        # previously there were 5
        with self.assertNumQueries(4):
            r = self.client.get(reverse("courses:course-retrieve-assigned", args=(self.course.id,)))
        self.assertEqual(r.status_code, status.HTTP_200_OK)


class CoursesSignupApiAccessTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("courses:course_signups-list")
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="test"
        )
        self.course = Course.objects.create(name="Test Course")
        self.data = {"user": self.user.id, "course": self.course.id}

    def test_unauthenticated_signup(self):
        response = self.client.post(self.list_url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signup(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CourseSignup.objects.filter(user=self.user, course=self.course).exists())

    def test_signup_for_the_same_course_second_time(self):
        CourseSignup.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"nonFieldErrors": ["Already signed up for this course."]}
        )

    def test_non_staff_access_to_different_user(self):
        User = get_user_model()
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="test"
        )
        other_user_signup = CourseSignup.objects.create(user=other_user, course=self.course)
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertNotIn(other_user_signup.id, [item["id"] for item in response.json()["results"]])

    def test_non_staff_access_to_own_signups(self):
        signup = CourseSignup.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertIn(signup.id, [item["id"] for item in response.json()["results"]])

    def test_staff_access_to_different_user_signups(self):
        User = get_user_model()
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="test"
        )
        other_user_signup = CourseSignup.objects.create(user=other_user, course=self.course)
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertIn(other_user_signup.id, [item["id"] for item in response.json()["results"]])

    def tearDown(self):
        self.course.cover_image.delete(save=True)
