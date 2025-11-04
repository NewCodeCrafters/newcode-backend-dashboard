"""
Custom permission classes for role-based access control.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class that allows access only to admin users (staff + superuser).
    """
    message = "You must be an admin to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.is_superuser
        )


class IsStaffUser(permissions.BasePermission):
    """
    Permission class that allows access to staff users (instructors/admins).
    """
    message = "You must be a staff member to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsStudentUser(permissions.BasePermission):
    """
    Permission class that allows access only to student users.
    """
    message = "You must be a student to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_student
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners to access their own objects,
    or admins to access any object.
    """
    message = "You can only access your own data."
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_staff and request.user.is_superuser:
            return True
        
        # Check if object has a 'user' or 'student' or 'staff' field
        if hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'staff'):
            return obj.staff == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        elif hasattr(obj, 'submitted_by'):
            return obj.submitted_by == request.user
        
        return False


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission class that allows owners to access their own objects,
    or staff members to access any object.
    """
    message = "You can only access your own data or you must be a staff member."
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if object has a 'user' or 'student' or 'staff' field
        if hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'staff'):
            return obj.staff == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        elif hasattr(obj, 'submitted_by'):
            return obj.submitted_by == request.user
        
        return False


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Permission class that allows read-only access to everyone,
    but write access only to admins.
    """
    message = "You must be an admin to modify this resource."
    
    def has_permission(self, request, view):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Allow write operations only for admins
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.is_superuser
        )


class CanManageExpenses(permissions.BasePermission):
    """
    Permission class for expense management.
    - Staff can submit and view expenses
    - Admins can approve, reject, and mark as paid
    """
    message = "You don't have permission to perform this action on expenses."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Staff can submit and view
        if view.action in ['list', 'retrieve', 'create']:
            return request.user.is_staff
        
        # Only admins can approve, reject, pay
        if view.action in ['approve', 'reject', 'mark_paid', 'destroy']:
            return request.user.is_staff and request.user.is_superuser
        
        # Update only if owner or admin
        if view.action in ['update', 'partial_update']:
            return request.user.is_staff
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff and request.user.is_superuser:
            return True
        
        # Staff can view any expense
        if view.action in ['retrieve']:
            return request.user.is_staff
        
        # Staff can only update their own pending expenses
        if view.action in ['update', 'partial_update']:
            return (
                request.user.is_staff and
                obj.submitted_by == request.user and
                obj.status == 'pending'
            )
        
        return False