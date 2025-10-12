from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Setup RBAC roles and permissions'
    
    def handle(self, *args, **kwargs):
        # Create groups (roles)
        student_group, created = Group.objects.get_or_create(name='Student')
        organizer_group, created = Group.objects.get_or_create(name='Organizer') 
        admin_group, created = Group.objects.get_or_create(name='Administrator')
        
        # Assign permissions based on your existing role logic
        student_perms = ['can_view_events', 'can_register_event']
        organizer_perms = ['can_view_events', 'can_create_event', 'can_edit_event', 'can_delete_event']
        admin_perms = ['can_approve_organizer'] + student_perms + organizer_perms
        
        # Assign permissions to groups
        for perm in student_perms:
            permission = Permission.objects.get(codename=perm)
            student_group.permissions.add(permission)
            
        for perm in organizer_perms:
            permission = Permission.objects.get(codename=perm)
            organizer_group.permissions.add(permission)
            
        for perm in admin_perms:
            permission = Permission.objects.get(codename=perm)
            admin_group.permissions.add(permission)
        
        self.stdout.write(self.style.SUCCESS('Roles and permissions have been set up successfully!'))