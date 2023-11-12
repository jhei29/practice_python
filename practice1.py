import logging
from datetime import datetime, timezone

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import mixins, generics, viewsets, views, status

from .permissions import IsTeacherUser, IsStudentUser
from .serializers import CustomTokenObtainPairSerializer

from users.models import User, UserProfile
from users.forms import CustomPasswordResetForm
from users.token import reset_password_token_generator
from users.serializers import (
    UserSerializer, UserProfileSerializer, ResetPasswordSerializer)

from grades.models import Course, Assignment, AssignmentGrade
from grades.serializers import (
    CourseSerializer, CoursePublicSerializer, AssignmentSerializer,
    AssignmentGradeSerializer, StudentGradebookSerializer,
    UploadAssignmentGradeSerializer)

from ratelimit.mixins import RatelimitMixin

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(RatelimitMixin, TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    ratelimit_key = 'post:username'
    ratelimit_rate = '5/s'
    ratelimit_block = True

    serializer_class = CustomTokenObtainPairSerializer


class ResetPasswordAPIView(RatelimitMixin, views.APIView):
    """
    API endpoint that allows admin users to reset passwords.
    """

    ratelimit_key = 'post:email'
    ratelimit_rate = '5/m'
    ratelimit_block = True

    serializer_class = ResetPasswordSerializer
    permission_classes = (IsAuthenticated, )

    token_generator = reset_password_token_generator
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            form = CustomPasswordResetForm(serializer.data)
            if form.is_valid():
                opts = {
                    'use_https': request.is_secure(),
                    'token_generator': self.token_generator,
                    'email_template_name': self.email_template_name,
                    'subject_template_name': self.subject_template_name,
                    'request': request,
                }
                form.save(**opts)
                return Response(
                    "Done. The password reset email has been sent!"
                    " If you don't receive an email check your spam folder.")

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(views.APIView):
    """
    API endpoint that allows the logged-in user profile to be viewed or edited.
    """

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        userprofile = request.user.userprofile
        username = kwargs.get('username')

        if username:
            userprofile = generics.get_object_or_404(
                UserProfile, user__username=username)

        serializer = self.serializer_class(userprofile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'userprofile'):
            serializer = self.serializer_class(request.user.userprofile)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_logger_message(self):
        message = '{datetime} {method} {action} {info}'
        format_string = {
            'datetime': datetime.now(timezone.utc).isoformat(),
            'method': self.request.method,
            'action': self.action,
            'info': self.request.user
        }

        if hasattr(self.request.user, 'userprofile'):
            format_string['info'] = self.request.user.userprofile.pk

        return message.format(**format_string)

    def retrieve(self, request, *args, **kwargs):

        # Admin users
        if bool(request.user and request.user.is_superuser):
            return super().retrieve(request, *args, **kwargs)

        logger.info(self.get_logger_message())
        return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):

        # Admin users
        if bool(request.user and request.user.is_superuser):
            return super().list(request, *args, **kwargs)

        logger.warning(self.get_logger_message())
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                         mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users' profile to be viewed or edited.
    """
    queryset = UserProfile.objects.all().order_by('-create_on')
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )

    def get_logger_message(self):
        message = '{datetime} {method} {action} {info}'
        format_string = {
            'datetime': datetime.now(timezone.utc).isoformat(),
            'method': self.request.method,
            'action': self.action,
            'info': self.request.user
        }

        if hasattr(self.request.user, 'userprofile'):
            format_string['info'] = self.request.user.userprofile.pk

        return message.format(**format_string)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows access only to teacher users.
        """
        if bool(request.user and request.user.is_staff):
            return super().retrieve(request, *args, **kwargs)

        logger.warning(self.get_logger_message())
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        """
        Allows access only to admin users.
        """
        if bool(request.user and request.user.is_superuser):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        logger.warning(self.get_logger_message())
        return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        """
        Allows access only to teacher users.
        """
        if bool(request.user and request.user.is_staff):
            return super().list(request, *args, **kwargs)

        logger.warning(self.get_logger_message())
        return Response(status=status.HTTP_403_FORBIDDEN)


class CourseReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing public courses.
    """
    queryset = Course.objects.filter(is_active=True).order_by('start_date')
    serializer_class = CoursePublicSerializer
    permission_classes = (AllowAny, )

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing courses.
    """
    serializer_class = CoursePublicSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """
        Returns the teacher or student enrolled course object.
        """

        # Teacher courses
        if bool(self.request.user.is_staff and not
                self.request.user.userprofile.is_student):
            # Teacher Course Serializer
            self.serializer_class = CourseSerializer
            return self.request.user.userprofile.course_set.all().order_by(
                'start_date')

        # Student courses
        return Course.objects.filter(
            enrollments=self.request.user.userprofile).order_by('start_date')

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AssignmentViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                        mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for getting course assignments.
    """
    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsTeacherUser]

        return [permission() for permission in self.permission_classes]

    def get_course_object(self):
        """
        Returns the teacher or student course object.
        """

        # Teacher
        if bool(self.request.user.is_staff
                and not self.request.user.userprofile.is_student):
            return generics.get_object_or_404(
                self.request.user.userprofile.course_set,
                pk=self.kwargs.get('course_pk'))

        # Student
        return generics.get_object_or_404(
            Course,
            pk=self.kwargs.get('course_pk'),
            enrollments=self.request.user.userprofile)

    def get_queryset(self):
        return Assignment.objects.filter(
            course=self.get_course_object()).order_by('due_date')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return generics.get_object_or_404(
            queryset, pk=self.kwargs.get('assignment_pk'))

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        course = self.get_course_object()
        request.data.update({'course': course.pk})
        return super().create(request, *args, **kwargs)


class AssignmentGradeViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin, mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """
    API endpoint for getting course assignments grade.
    """
    serializer_class = AssignmentGradeSerializer
    permission_classes = (IsAuthenticated, IsTeacherUser)

    def get_course_object(self):
        """
        Returns the teacher course object.
        """
        return generics.get_object_or_404(
            self.request.user.userprofile.course_set,
            pk=self.kwargs.get('course_pk'))

    def get_queryset(self):
        return AssignmentGrade.objects.filter(
            assignment__course=self.get_course_object()
        ).order_by('assignment__due_date')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return generics.get_object_or_404(
            queryset, pk=self.kwargs.get('pk'))

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        course = self.get_course_object()
        request.data.update({'course': course.pk})
        return super().create(request, *args, **kwargs)


class StudentGradebookListAPIView(generics.ListAPIView):
    """
    API endpoint for getting course assignments.
    """
    serializer_class = StudentGradebookSerializer
    permission_classes = (IsAuthenticated, IsStudentUser)

    def get_course_object(self):
        """
        Returns the student course object.
        """
        return generics.get_object_or_404(
            Course,
            pk=self.kwargs.get('course_pk'),
            enrollments=self.request.user.userprofile)

    def get_queryset(self):
        return Assignment.objects.filter(
            course=self.get_course_object()).order_by('due_date')

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AssignmentGradeUploadAPIView(generics.UpdateAPIView):
    """
    API endpoint for upload assignments file.
    """
    serializer_class = UploadAssignmentGradeSerializer
    permission_classes = (IsAuthenticated, IsStudentUser)

    def get_queryset(self):
        return AssignmentGrade.objects.filter(
            student=self.request.user.userprofile
        ).order_by('assignment__due_date')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return generics.get_object_or_404(
            queryset, pk=self.kwargs.get('pk'))

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
