from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='financial_aid/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.student_register, name='student_register'),
    
    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Manager Management
    path('managers/register/', views.register_manager, name='register_manager'),
    path('managers/list/', views.manage_managers, name='manage_managers'),
    
    # Application Management
    path('applications/create/', views.apply_for_aid, name='apply_for_aid'),
    path('applications/review/<int:application_id>/', views.review_application, name='review_application'),
    path('applications/list/', views.manage_applications, name='manage_applications'),
]