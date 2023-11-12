from django.urls import include, path
from rest_framework import routers

from .views import (
    CustomTokenObtainPairView, UserProfileAPIView, ResetPasswordAPIView,
    UserViewSet, UserProfileViewSet, CourseReadOnlyModelViewSet,
    CourseViewSet, AssignmentViewSet, AssignmentGradeViewSet,
    StudentGradebookListAPIView, AssignmentGradeUploadAPIView)

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'courses-public', CourseReadOnlyModelViewSet)


app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('comment/', include('comments.urls')),
    path('token/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('profile/<uuid:pk>/', UserProfileAPIView.as_view(),
         name='api-your-profile'),
    path('course/', CourseViewSet.as_view({'get': 'list'}),
         name='api-your-courses'),
    path('course/<int:pk>/', CourseViewSet.as_view({'get': 'retrieve'}),
         name='api-your-course-details'),
    path('course/<int:course_pk>/assignments/',
         AssignmentViewSet.as_view({
                                   'get': 'list',
                                   'post': 'create'}),
         name='api-your-course-assignments'),
    path('course/<int:course_pk>/assignment/<int:assignment_pk>/',
         AssignmentViewSet.as_view({'get': 'retrieve'}),
         name='api-your-course-assignment-details'),
    path('course/<int:course_pk>/assignment-grade/',
         AssignmentGradeViewSet.as_view({
                                        'get': 'list',
                                        'post': 'create'}),
         name='api-course-student-assignment-grade'),
    path('course/<int:course_pk>/assignment-grade/<int:pk>/',
         AssignmentGradeViewSet.as_view({
                                        'get': 'retrieve',
                                        'put': 'update'}),
         name='api-course-student-assignment-grade'),
    path('course/<int:course_pk>/gradebook/',
         StudentGradebookListAPIView.as_view(),
         name='api-student-gradebook'),
    path('assignment-grade/<int:pk>/upload/',
         AssignmentGradeUploadAPIView.as_view(),
         name='api-assignment-file-upload'),
    path('reset-password/', ResetPasswordAPIView.as_view(),
         name='api-reset-password'),
]
