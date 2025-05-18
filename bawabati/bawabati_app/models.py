from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# Validator for file uploads
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.docx', '.pptx']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

def get_default_end_date():
    return timezone.now().date() + timezone.timedelta(days=90)

# User profile with role-based access
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile ({self.role})"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

def get_default_instructor():
    return User.objects.filter(userprofile__role='teacher').first()

# Course model assigned to a teacher
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses_teaching',
        limit_choices_to={'userprofile__role': 'teacher'},
        null=True,
        blank=True
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=get_default_end_date)
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.enrollments.count()

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError(_('End date must be after start date'))
        
        if self.instructor:
            # Use get_or_create to ensure profile exists
            profile, created = UserProfile.objects.get_or_create(
                user=self.instructor,
                defaults={'role': 'teacher'}
            )
            if profile.role != 'teacher':
                raise ValidationError(_('Instructor must be a teacher'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Notes uploaded by teachers (or admin)
class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    file = models.FileField(upload_to='notes/', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        if not self.content and not self.file:
            raise ValidationError('Either content or file must be provided')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Enrollment for students
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
from django.contrib.auth.models import User
from django.db import models

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    major = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
