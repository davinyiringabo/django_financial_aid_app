from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import StudentRegistrationForm, ManagerRegistrationForm, FinancialAidApplicationForm
from .models import FinancialAidApplication, User
from .decorators import admin_required, manager_required, student_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta

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
        print('Register', form)
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
    applications_list = FinancialAidApplication.objects.all().order_by('-application_date')
    
    # Pagination
    paginator = Paginator(applications_list, 10)
    page = request.GET.get('page')
    applications = paginator.get_page(page)
    
    # Get monthly application counts for the last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_stats = (
        applications_list
        .filter(application_date__gte=six_months_ago)
        .annotate(month=TruncMonth('application_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Prepare data for charts
    monthly_labels = [stat['month'].strftime('%B %Y') for stat in monthly_stats]
    monthly_data = [stat['count'] for stat in monthly_stats]
    
    context = {
        'applications': applications,
        'pending_count': applications_list.filter(status='pending').count(),
        'approved_count': applications_list.filter(status='approved').count(),
        'rejected_count': applications_list.filter(status='rejected').count(),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': monthly_data,
    }
    return render(request, 'financial_aid/manager_dashboard.html', context)

@login_required
@admin_required
def admin_dashboard(request):
    applications = FinancialAidApplication.objects.all().order_by('-application_date')
    managers = User.objects.filter(user_type='manager')
    students = User.objects.filter(user_type='student')
    
    pending_count = applications.filter(status='pending').count()
    approved_count = applications.filter(status='approved').count()
    rejected_count = applications.filter(status='rejected').count()
    
    context = {
        'applications': applications,
        'managers': managers,
        'active_managers': managers.filter(is_active=True).count(),
        'inactive_managers': managers.filter(is_active=False).count(),
        'student_count': students.count(),
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'financial_aid/admin_dashboard.html', context) 