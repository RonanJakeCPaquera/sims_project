from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    course = models.CharField(max_length=100)
    year_level = models.IntegerField(choices=YEAR_CHOICES)
    birthdate = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Course(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    units = models.PositiveIntegerField()
    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=50)
    department = models.CharField(max_length=100, blank=True, null=True)
    course_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructor_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.code} - {self.course.name}"
    
class Grade(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    midterm_grade = models.IntegerField(null=True, blank=True)
    finals_grade = models.IntegerField(null=True, blank=True)
    overall_grade = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Grades for {self.enrollment.student.username} in {self.enrollment.course.code}"
