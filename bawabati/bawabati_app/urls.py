from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from . import views
from .views import (
    UserList, UserDetail,
    CourseList, CourseDetail,
    EnrollmentList, EnrollmentDetail,
    UserProfileAPI, CurrentUserView, CSRFTokenView, DashboardStatsView ,StudentListView, StudentDetailView
)

def logout_view(request):
    auth_logout(request)
    return redirect('login')

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='bawabati_app/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard & Profile
    path('', views.dashboard, name='dashboard'),
    path('my-profile/', views.profile, name='profile'),
    
    # User Management (Admin)
    path('manage/users/', views.UserListView.as_view(), name='user_list'),
    path('manage/users/add/', views.UserCreateView.as_view(), name='user_create'),
    path('manage/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('manage/users/<int:pk>/remove/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Course Management
    path('my-courses/', views.CourseListView.as_view(), name='course_list'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('manage/courses/add/', views.CourseCreateView.as_view(), name='course_create'),
    path('manage/courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('manage/courses/<int:pk>/remove/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # Enrollment
    path('course/<int:pk>/join/', views.enroll_course, name='enroll_course'),
    
    # Notes
    path('course/notes/add/', views.NoteCreateView.as_view(), name='note_create'),
    path('course/notes/<int:pk>/remove/', views.NoteDeleteView.as_view(), name='note_delete'),
    
    # API URLs - Authentication/User 
   path('api/csrf/', CSRFTokenView.as_view(), name='api-csrf-token'),

    path('api/current-user/', CurrentUserView.as_view(), name='api-current-user'),
    path('api/dashboard-stats/', DashboardStatsView.as_view(), name='api-dashboard-stats'),
    path('api/profile/', UserProfileAPI.as_view(), name='api-profile'),
    path('api/users/', UserList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('api/students/', StudentListView.as_view(), name='student-list'),
    path('api/students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),

    # API URLs - Courses and Enrollments
    path('api/courses/', CourseList.as_view(), name='course-list'),
    path('api/courses/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    path('api/enrollments/', EnrollmentList.as_view(), name='enrollment-list'),
    path('api/enrollments/<int:pk>/', EnrollmentDetail.as_view(), name='enrollment-detail'),
] 