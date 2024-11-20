from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from .forms import StudentRegistrationForm, ManagerRegistrationForm, FinancialAidApplicationForm
from .models import FinancialAidApplication, User
from .decorators import admin_required, manager_required, student_required

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'financial_aid/student_register.html', {'form': form})

@admin_required
def register_manager(request):
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manager account created successfully')
            return redirect('admin_dashboard')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'financial_aid/register_manager.html', {'form': form})

@student_required
def apply_for_aid(request):
    if request.method == 'POST':
        form = FinancialAidApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user.student
            application.save()
            messages.success(request, 'Application submitted successfully')
            return redirect('student_dashboard')
    else:
        form = FinancialAidApplicationForm()
    return render(request, 'financial_aid/apply.html', {'form': form})

@manager_required
def review_application(request, application_id):
    application = FinancialAidApplication.objects.get(id=application_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        application.status = status
        application.review_notes = notes
        application.reviewed_by = request.user
        application.review_date = timezone.now()
        application.save()
        
        messages.success(request, 'Application reviewed successfully')
        return redirect('manager_dashboard')
    
    return render(request, 'financial_aid/review_application.html', {'application': application})

@admin_required
def manage_applications(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        
        application = FinancialAidApplication.objects.get(id=application_id)
        application.is_active = (action == 'activate')
        application.save()
        
        messages.success(request, f'Application {action}d successfully')
    
    applications = FinancialAidApplication.objects.all()
    return render(request, 'financial_aid/manage_applications.html', {'applications': applications})

@admin_required
def manage_managers(request):
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        action = request.POST.get('action')
        
        manager = User.objects.get(id=manager_id, user_type='manager')
        manager.is_active = (action == 'activate')
        manager.save()
        
        messages.success(request, f'Manager account {action}d successfully')
    
    managers = User.objects.filter(user_type='manager')
    return render(request, 'financial_aid/manage_managers.html', {'managers': managers})

@login_required
def dashboard(request):
    if request.user.user_type == 'student':
        return student_dashboard(request)
    elif request.user.user_type == 'manager':
        return manager_dashboard(request)
    elif request.user.user_type == 'admin':
        return admin_dashboard(request)
    return redirect('login')

@login_required
@student_required
def student_dashboard(request):
    applications = FinancialAidApplication.objects.filter(student__user=request.user)
    context = {
        'applications': applications,
        'pending_count': applications.filter(status='pending').count(),
        'approved_count': applications.filter(status='approved').count(),
        'rejected_count': applications.filter(status='rejected').count(),
    }
    return render(request, 'financial_aid/student_dashboard.html', context)

@login_required
@manager_required
def manager_dashboard(request):
    applications = FinancialAidApplication.objects.all()
    context = {
        'applications': applications,
        'pending_count': applications.filter(status='pending').count(),
        'approved_count': applications.filter(status='approved').count(),
        'rejected_count': applications.filter(status='rejected').count(),
    }
    return render(request, 'financial_aid/manager_dashboard.html', context)

@login_required
@admin_required
def admin_dashboard(request):
    applications = FinancialAidApplication.objects.all().order_by('-application_date')
    managers = User.objects.filter(user_type='manager')
    students = User.objects.filter(user_type='student')
    
    context = {
        'applications': applications,
        'managers': managers,
        'active_managers': managers.filter(is_active=True).count(),
        'inactive_managers': managers.filter(is_active=False).count(),
        'student_count': students.count(),
        'pending_count': applications.filter(status='pending').count(),
        'approved_count': applications.filter(status='approved').count(),
        'rejected_count': applications.filter(status='rejected').count(),
    }
    return render(request, 'financial_aid/admin_dashboard.html', context) 