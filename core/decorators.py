from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if hasattr(request.user, 'groups'):
                group = None
                if request.user.groups.exists():
                    group = request.user.groups.all()[0].name
                if group in allowed_roles:
                    return view_func(request, *args, **kwargs)
            return redirect('dashboard')
        return wrapper_func
    return decorator
