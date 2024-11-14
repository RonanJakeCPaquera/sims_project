from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .forms import StudentRegistrationForm, StudentProfileForm, FacultyRegistrationForm
from .models import StudentProfile, FacultyProfile

def home(request):
    return render(request, 'base/home.html')

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('base:faculty_dashboard')
        return redirect('base:student_dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
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
        if request.user.is_staff:  # Faculty users
            return redirect('base:faculty_dashboard')
        return redirect('base:student_dashboard')  # Changed from student_profile
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Check if user exists
            user = User.objects.get(username=username)
            # Try to authenticate
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect based on user type
                if user.is_staff:  # Faculty users
                    return redirect('base:faculty_dashboard')
                return redirect('base:student_dashboard')  # Changed from student_profile
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
def student_dashboard(request):  # Renamed from student_profile
    if request.user.is_staff:  # Prevent faculty from accessing student dashboard
        return redirect('base:faculty_dashboard')
        
    try:
        student = request.user.student_profile
        context = {
            'student': student,
            'student_name': request.user.get_full_name()
        }
        return render(request, 'base/student_dashboard.html', context)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('base:login')

def faculty_register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('base:admin_home')
        return redirect('base:student_profile')
    
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
        context = {
            'faculty_profile': faculty_profile,
            'students': students,
            'faculty_name': request.user.get_full_name(),
            'department': faculty_profile.department
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
            Q(user__last_name__icontains=query) |
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
            # Create User instance
            user = User.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password1'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Create StudentProfile
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
            # Update User information
            student.user.first_name = request.POST.get('first_name')
            student.user.last_name = request.POST.get('last_name')
            student.user.save()
            
            # Update StudentProfile information
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
