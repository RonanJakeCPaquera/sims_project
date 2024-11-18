from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('faculty-register/', views.faculty_register_view, name='admin_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/add-student/', views.add_student, name='add_student'),
    path('faculty/edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('faculty/delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('faculty/search/', views.search_students, name='search_students'),
    path('faculty/filter/', views.filter_students, name='filter_students'),
    path('update-profile/', views.update_student_profile, name='update_profile'),
    path('faculty/add-course/', views.create_course, name='add_course'),
    path('update_course/<int:pk>/', views.update_course, name='update_course'),
    path('delete_course/<int:pk>/', views.delete_course, name='delete_course'),
]
