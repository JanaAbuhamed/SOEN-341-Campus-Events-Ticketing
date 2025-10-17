from rest_framework import permissions

class CanViewEvents(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all authenticated users (students, organizers, admins)
        return request.user.is_authenticated


class CanCreateEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('main.can_create_event')

class CanEditEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('main.can_edit_event')

class CanDeleteEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('main.can_delete_event')

class CanRegisterEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('main.can_register_event')

class CanViewUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('main.can_view_users') or request.user.has_perm('main.can_view_events')
