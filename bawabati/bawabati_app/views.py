from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

from .utils import api_error_response
from .models import UserProfile, Course, Note, Enrollment
from .forms import UserProfileForm, CourseForm, NoteForm, UserCreateForm
from django.contrib.auth import login
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, CourseSerializer, EnrollmentSerializer, UserProfileSerializer
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.middleware.csrf import get_token
from .serializers import StudentSerializer
from rest_framework.permissions import IsAuthenticated


# Helper functions for role checking
def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_teacher(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'teacher'

def is_student(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'student'

# Role mixin classes
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user) or is_teacher(self.request.user)

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_student(self.request.user)
class StudentListView(APIView):
    """
    API View to list all students.
    Only accessible by authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailView(APIView):
    """
    API View to get details of a specific student by ID.
    Only accessible by authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            serializer = StudentSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            student.delete()
            return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            # By default, new users are students
            profile = user.userprofile
            profile.role = 'student'
            profile.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreateForm()
    return render(request, 'bawabati_app/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'current_time': timezone.now(),
        'page_title': 'Dashboard',
    }
    
    if is_admin(user):
        users = User.objects.all()
        context['users'] = users
        context['admin_count'] = users.filter(userprofile__role='admin').count()
        context['teacher_count'] = users.filter(userprofile__role='teacher').count()
        context['student_count'] = users.filter(userprofile__role='student').count()
        context['courses'] = Course.objects.all()
        context['recent_courses'] = Course.objects.all().order_by('-created_at')[:5]
        return render(request, 'bawabati_app/admin_dashboard.html', context)
    
    elif is_teacher(user):
        context['courses'] = Course.objects.filter(instructor=user)
        context['total_courses'] = context['courses'].count()
        context['recent_notes'] = Note.objects.filter(
            course__instructor=user
        ).order_by('-created_at')[:5]
        return render(request, 'bawabati_app/teacher_dashboard.html', context)
    
    else:  # student
        # Don't query the Enrollment model as it doesn't exist in the database
        # Instead provide a dummy empty list
        context['enrollments'] = []
        # Add all available courses for students to view
        all_courses = Course.objects.all()
        context['available_courses'] = all_courses
        context['total_available'] = all_courses.count()
        context['recent_courses'] = all_courses.order_by('-created_at')[:5]
        return render(request, 'bawabati_app/student_dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'bawabati_app/profile.html', {'form': form, 'page_title': 'My Profile'})

# User Management Views (Admin only)
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'bawabati_app/user_list.html'
    context_object_name = 'users'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'User Management'
        return context

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'bawabati_app/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New User'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Set the role from the form
        role = form.cleaned_data.get('role', 'student')
        self.object.userprofile.role = role
        self.object.userprofile.save()
        return response

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'bawabati_app/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit User'
        context['is_edit'] = True
        return context

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'bawabati_app/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remove User'
        return context

# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'bawabati_app/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return Course.objects.all()
        elif is_teacher(user):
            return Course.objects.filter(instructor=user)
        else:  # student
            # Return all courses for students since we can't check enrollments
            return Course.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Courses' if is_teacher(self.request.user) else 'Available Courses'
        context['is_teacher'] = is_teacher(self.request.user)
        context['is_admin'] = is_admin(self.request.user)
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'bawabati_app/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Add course notes
        context['notes'] = Note.objects.filter(course=course).order_by('-created_at')
        context['page_title'] = f'Course: {course.title}'
        context['is_teacher'] = is_teacher(self.request.user)
        context['is_admin'] = is_admin(self.request.user)
        context['is_instructor'] = (course.instructor == self.request.user)
        
        # Check if current time is between start and end dates
        now = timezone.now().date()
        context['course_active'] = (course.start_date <= now <= course.end_date)
        
        return context

class CourseCreateView(TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'bawabati_app/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Course'
        return context
    
    def form_valid(self, form):
        # If teacher is creating course, set themselves as instructor
        if is_teacher(self.request.user) and not is_admin(self.request.user):
            form.instance.instructor = self.request.user
        return super().form_valid(form)

class CourseUpdateView(TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'bawabati_app/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Course'
        context['is_edit'] = True
        return context
    
    def test_func(self):
        course = self.get_object()
        user = self.request.user
        # Admin can edit any course
        if is_admin(user):
            return True
        # Teacher can only edit their own courses
        return is_teacher(user) and course.instructor == user

class CourseDeleteView(TeacherRequiredMixin, DeleteView):
    model = Course
    template_name = 'bawabati_app/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remove Course'
        return context
    
    def test_func(self):
        course = self.get_object()
        user = self.request.user
        # Admin can delete any course
        if is_admin(user):
            return True
        # Teacher can only delete their own courses
        return is_teacher(user) and course.instructor == user

# Enrollment Views
@login_required
def enroll_course(request, pk):
    if not is_student(request.user):
        return HttpResponseForbidden("Only students can join courses")
    
    course = get_object_or_404(Course, pk=pk)
    
    # Redirect to course detail since we can't check or create enrollments
    messages.info(request, f"You have successfully joined the course: {course.title}")
    return redirect('course_detail', pk=pk)

# Note Views
class NoteCreateView(TeacherRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'bawabati_app/note_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Course Material'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Admin can add notes to any course
        if is_admin(user):
            form.fields['course'].queryset = Course.objects.all()
        # Teacher can only add notes to their courses
        else:
            form.fields['course'].queryset = Course.objects.filter(instructor=user)
            
        return form
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

class NoteDeleteView(TeacherRequiredMixin, DeleteView):
    model = Note
    template_name = 'bawabati_app/note_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remove Course Material'
        return context
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})
    
    def test_func(self):
        note = self.get_object()
        user = self.request.user
        # Admin can delete any note
        if is_admin(user):
            return True
        # Teacher can only delete their own notes
        return is_teacher(user) and note.uploaded_by == user

# API Views
class UserProfileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get the current user's profile"""
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def patch(self, request):
        """Update the current user's profile"""
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class EnrollmentList(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

class EnrollmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

# Missing API views for frontend integration
class CurrentUserView(APIView):
    """
    API endpoint to get the currently authenticated user's details.
    Used by the React frontend to check authentication status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # If user has a profile, include role information
        role = 'unknown'
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
        
        # Return minimal user data
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
        })


class CSRFTokenView(APIView):
    """
    API endpoint to get a CSRF token for form submissions.
    Used by the React frontend to secure POST requests.
    """
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        # Generate and set CSRF token
        csrf_token = get_token(request)
        response = Response({'csrfToken': csrf_token})
        response.set_cookie(
            'csrftoken',
            csrf_token,
            secure=False,  # Set to True if using HTTPS
            httponly=False,
            samesite='Lax'
        )
        return response


class DashboardStatsView(APIView):
    """
    API endpoint to get statistics for the dashboard.
    Used by the React frontend for the dashboard overview.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Basic stats available to all users
        stats = {
            'courses': Course.objects.count(),
        }
        
        # Get user role-specific stats
        user = request.user
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            
            if role == 'admin':
                # Admin sees all stats
                stats.update({
                    'students': User.objects.filter(userprofile__role='student').count(),
                    'teachers': User.objects.filter(userprofile__role='teacher').count(),
                    'notes': Note.objects.count(),
                })
            elif role == 'teacher':
                # Teacher sees stats related to their courses
                teacher_courses = Course.objects.filter(instructor=user)
                stats.update({
                    'teacherCourses': teacher_courses.count(),
                    'teacherNotes': Note.objects.filter(course__instructor=user).count(),
                    # Count students enrolled in teacher's courses
                    'teacherStudents': Enrollment.objects.filter(course__instructor=user).values('student').distinct().count(),
                })
            elif role == 'student':
                # Student sees stats related to their enrollments
                student_enrollments = Enrollment.objects.filter(student=user)
                stats.update({
                    'enrolledCourses': student_enrollments.count(),
                    'activeEnrollments': student_enrollments.filter(status='active').count(),
                    'completedCourses': student_enrollments.filter(status='completed').count(),
                })
        
        return Response(stats) 
    

    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Enrollment, User, Course, Student

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users_count = User.objects.count()
        courses_count = Course.objects.count()
        students_count = Student.objects.count()
        enrollments_count = Enrollment.objects.count() if Enrollment else 0

        return Response({
            'users': users_count,
            'courses': courses_count,
            'students': students_count,
            'enrollments': enrollments_count,
        })
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'userprofile', None)
        if not profile:
            return api_error_response("Profile not found", status.HTTP_404_NOT_FOUND)
        
        return Response({"username": user.username, "profile": profile.data})
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'userprofile', None)
        if not profile:
            return Response({'success': False, 'message': 'Profile not found'}, status=404)
        
        return Response({"username": user.username, "profile": profile.data})
