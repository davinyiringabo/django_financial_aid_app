from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'student':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Student privileges required.')
        return redirect('login')
    return wrapper

def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'manager':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Manager privileges required.')
        return redirect('login')
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    return wrapper 