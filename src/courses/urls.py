from rest_framework.routers import SimpleRouter

from courses.views import CourseViewSet, CourseSignupView

app_name = "courses"

router = SimpleRouter()
router.register("courses", CourseViewSet)
router.register("course-signups", CourseSignupView, basename="course_signups")

urlpatterns = router.urls
