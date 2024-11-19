from django.contrib import admin

from django.contrib import admin
from .models import Course, FacultyProfile, StudentProfile

admin.site.register(StudentProfile)
admin.site.register(FacultyProfile)
admin.site.register(Course)
