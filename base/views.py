from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .forms import StudentRegistrationForm, StudentProfileForm, FacultyRegistrationForm
from .models import Enrollment, StudentProfile, FacultyProfile, Course

def home(request):
    return render(request, 'base/home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('base:faculty_dashboard' if request.user.is_staff else 'base:student_dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Student registration successful! Please login.')
                return redirect('base:login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentRegistrationForm()
    return render(request, 'base/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('base:faculty_dashboard' if request.user.is_staff else 'base:student_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('base:faculty_dashboard' if user.is_staff else 'base:student_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist.')
    
    return render(request, 'base/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('base:login')

@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('base:faculty_dashboard')
        
    try:
        student = request.user.student_profile
        enrollments = Enrollment.objects.filter(student=request.user).select_related('grade', 'course')
        total_units = sum(enrollment.course.units for enrollment in enrollments)
        context = {
            'student': student,
            'student_name': request.user.get_full_name(),
            'enrollments': enrollments,
            'total_units': total_units
        }
        return render(request, 'base/student_dashboard.html', context)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('base:login')

def faculty_register_view(request):
    if request.user.is_authenticated:
        return redirect('base:admin_home' if request.user.is_staff else 'base:student_profile')
    
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty registration successful! Please login.')
            return redirect('base:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = FacultyRegistrationForm()
    return render(request, 'base/admin_register.html', {'form': form})

@staff_member_required(login_url='base:login')
def faculty_dashboard(request):
    try:
        faculty_profile = request.user.faculty_profile
        students = StudentProfile.objects.all().order_by('student_id')
        courses = Course.objects.all()
        selected_course_id = request.GET.get('course')
        
        enrollments = Enrollment.objects.filter(course_id=selected_course_id) if selected_course_id else Enrollment.objects.all()
        
        context = {
            'faculty_profile': faculty_profile,
            'students': students,
            'faculty_name': request.user.get_full_name(),
            'department': faculty_profile.department,
            'total_students': students.count(),
            'total_courses': courses.count(),
            'courses': courses,
            'enrollments': enrollments,
            'selected_course_id': selected_course_id
        }
        return render(request, 'base/faculty_dashboard.html', context)
    except FacultyProfile.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('base:login')

@staff_member_required(login_url='base:login')
def update_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student record updated successfully!')
            return redirect('base:admin_home')
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'base/update_student.html', {'form': form, 'student': student})

@staff_member_required(login_url='base:login')
def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, 'Student record deleted successfully!')
    return redirect('base:admin_home')

@staff_member_required(login_url='base:login')
def search_students(request):
    query = request.GET.get('q', '')
    try:
        faculty_profile = request.user.faculty_profile
        students = StudentProfile.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontai=query) |
            Q(student_id__icontains=query) |
            Q(course__icontains=query)
        ).order_by('student_id')
        
        context = {
            'faculty_profile': faculty_profile,
            'students': students,
            'faculty_name': request.user.get_full_name(),
            'department': faculty_profile.department,
            'query': query
        }
        return render(request, 'base/faculty_dashboard.html', context)
    except FacultyProfile.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('base:login')

@staff_member_required(login_url='base:login')
def filter_students(request):
    course = request.GET.get('course')
    year_level = request.GET.get('year_level')
    
    try:
        faculty_profile = request.user.faculty_profile
        students = StudentProfile.objects.all()
        
        if course:
            students = students.filter(course=course)
        if year_level:
            students = students.filter(year_level=year_level)
            
        context = {
            'faculty_profile': faculty_profile,
            'students': students,
            'faculty_name': request.user.get_full_name(),
            'department': faculty_profile.department,
            'selected_course': course,
            'selected_year': year_level
        }
        return render(request, 'base/faculty_dashboard.html', context)
    except FacultyProfile.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('base:login')

@staff_member_required(login_url='base:login')
def add_student(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password1'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            StudentProfile.objects.create(
                user=user,
                student_id=request.POST.get('student_id'),
                course=request.POST.get('course'),
                year_level=request.POST.get('year_level'),
                birthdate=request.POST.get('birthdate'),
                contact_number=request.POST.get('contact_number'),
                address=request.POST.get('address')
            )
            
            messages.success(request, f'Student {user.get_full_name()} has been successfully added!')
            return redirect('base:faculty_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
            return render(request, 'base/add_student.html')
            
    return render(request, 'base/add_student.html')

@staff_member_required(login_url='base:login')
def edit_student(request, student_id):
    try:
        student = get_object_or_404(StudentProfile, id=student_id)
        if request.method == 'POST':
            student.user.first_name = request.POST.get('first_name')
            student.user.last_name = request.POST.get('last_name')
            student.user.save()
            
            student.student_id = request.POST.get('student_id')
            student.course = request.POST.get('course')
            student.year_level = request.POST.get('year_level')
            student.birthdate = request.POST.get('birthdate')
            student.contact_number = request.POST.get('contact_number')
            student.address = request.POST.get('address')
            student.save()
            
            messages.success(request, 'Student information updated successfully!')
            return redirect('base:faculty_dashboard')
            
        context = {
            'student': student,
            'faculty_name': request.user.get_full_name(),
            'department': request.user.faculty_profile.department
        }
        return render(request, 'base/edit_student.html', context)
        
    except Exception as e:
        messages.error(request, f'Error updating student: {str(e)}')
        return redirect('base:faculty_dashboard')

@login_required
def update_student_profile(request):
    if request.user.is_staff:
        return redirect('base:faculty_dashboard')
        
    try:
        student = request.user.student_profile
        if request.method == 'POST':
            student.contact_number = request.POST.get('contact_number')
            student.address = request.POST.get('address')
            student.save()
            messages.success(request, 'Profile updated successfully!')
        return redirect('base:student_dashboard')
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('base:login')
    
def display_courses(request):
    courses = Course.objects.all()
    return render(request, 'base/add_course.html', {'courses': courses})

@staff_member_required(login_url='base:login')
def create_course(request):
    if request.method == 'POST':
        course = Course.objects.create(
            code=request.POST['code'], 
            name=request.POST['name'], 
            units=request.POST['units'], 
            semester=request.POST['semester'], 
            academic_year=request.POST['academic_year'],
            department=request.POST.get('department', ''),
            course_type=request.POST.get('course_type', ''),
            description=request.POST.get('description', ''),
            instructor_name=request.POST.get('instructor_name', '')
        )
        
        messages.success(request, f'Course {course.code} - {course.name} added successfully!')
        return redirect('base:faculty_dashboard')
    
    return render(request, 'base/add_course.html', {'course': {}, 'create': True})

@staff_member_required(login_url='base:login')
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.code = request.POST['code']
        course.name = request.POST['name']
        course.units = request.POST['units']
        course.semester = request.POST['semester']
        course.academic_year = request.POST['academic_year']
        course.department = request.POST.get('department', '')
        course.course_type = request.POST.get('course_type', '')
        course.description = request.POST.get('description', '')
        course.instructor_name = request.POST.get('instructor_name', '')
        course.save()
        messages.success(request, f'Course {course.code} - {course.name} updated successfully!')
        return redirect('base:faculty_dashboard')
    
    return render(request, 'base/add_course.html', {'course': course, 'update': True})

@staff_member_required(login_url='base:login')
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('base:faculty_dashboard')

@staff_member_required(login_url='base:login')
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('grade', 'student')
    context = {
        'course': course,
        'enrollments': enrollments
    }
    return render(request, 'base/course_detail.html', context)

@staff_member_required(login_url='base:login')
def enroll_student(request, course_id=None):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        course_id = request.POST.get('course_id', course_id)
        student = get_object_or_404(User, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        
        Enrollment.objects.create(student=student, course=course)
        
        messages.success(request, f'Student {student.username} enrolled in {course.code} - {course.name} successfully!')
        return redirect('base:course_detail', course_id=course.id)
    
    students = User.objects.filter(is_staff=False)
    courses = Course.objects.all()
    context = {
        'students': students,
        'courses': courses,
        'selected_course_id': course_id
    }
    return render(request, 'base/enroll_student.html', context)

@staff_member_required(login_url='base:login')
def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, enrollment_id=enrollment_id)
    enrollment.delete()
    messages.success(request, 'Enrollment deleted successfully!')
    return redirect('base:faculty_dashboard')

def admin_home(request):
    # Your logic for the admin home view
    return render(request, 'base/admin_home.html')

#grades
from .models import Grade

@staff_member_required(login_url='base:login')
def add_grade(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, enrollment_id=enrollment_id)
    if request.method == 'POST':
        midterm_grade = request.POST.get('midterm_grade') or None
        finals_grade = request.POST.get('finals_grade') or None
        overall_grade = request.POST.get('overall_grade') or None
        
        if midterm_grade:
            midterm_grade = float(midterm_grade)
        if finals_grade:
            finals_grade = float(finals_grade)
        if overall_grade:
            overall_grade = float(overall_grade)
        
        # Check if a grade already exists for this enrollment
        if Grade.objects.filter(enrollment=enrollment).exists():
            messages.error(request, 'Grade already exists for this enrollment.')
        else:
            Grade.objects.create(
                enrollment=enrollment,
                midterm_grade=midterm_grade,
                finals_grade=finals_grade,
                overall_grade=overall_grade
            )
            messages.success(request, 'Grade added successfully!')
        
        return redirect('base:course_detail', course_id=enrollment.course.id)
    return render(request, 'base/add_grade.html', {'enrollment': enrollment})

@staff_member_required(login_url='base:login')
def update_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.midterm_grade = request.POST.get('midterm_grade')
        grade.finals_grade = request.POST.get('finals_grade')
        grade.overall_grade = request.POST.get('overall_grade')
        grade.save()
        messages.success(request, 'Grade updated successfully!')
        return redirect('base:course_detail', course_id=grade.enrollment.course.id)
    return render(request, 'base/update_grade.html', {'grade': grade})

@staff_member_required(login_url='base:login')
def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    course_id = grade.enrollment.course.id
    grade.delete()
    messages.success(request, 'Grade deleted successfully!')
    return redirect('base:course_detail', course_id=course_id)

