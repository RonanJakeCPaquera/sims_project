from django.contrib import admin

from django.contrib import admin
from .models import Course, Enrollment, FacultyProfile, Grade, StudentProfile

admin.site.register(StudentProfile)
admin.site.register(FacultyProfile)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Grade)
