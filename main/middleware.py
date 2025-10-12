from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

class RoleAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip auth for public pages
        public_paths = [
            reverse('loginindex'),
            reverse('signup'), 
            reverse('studentlogin'),
            reverse('organizerlogin'),
            reverse('adminlogin'),
            '/api/register/',
            '/api/login/',
        ]
        
        if request.path in public_paths:
            return None
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            return redirect('loginindex')
        
        # Role-based authorization
        user = request.user
        
        # Student routes
        student_paths = ['/api/events/', '/student-dashboard/']
        if any(request.path.startswith(path) for path in student_paths):
            if user.role != 0:
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Students only'}, status=403)
                return redirect('loginindex')
        
        # Organizer routes  
        organizer_paths = ['/organizer-dashboard/', '/organizer/events/']
        if any(request.path.startswith(path) for path in organizer_paths):
            if user.role != 1 or user.status != 1:  # Must be approved organizer
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Approved organizers only'}, status=403)
                return redirect('loginindex')
        
        # Admin routes
        admin_paths = ['/admin-dashboard/', '/admin/approve/']
        if any(request.path.startswith(path) for path in admin_paths):
            if user.role != 2:  # Must be admin
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Admins only'}, status=403)
                return redirect('loginindex')
        
        return None