"""
Utility functions for common operations across the application.
"""
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal

from .models import Notification, OfficeExpense, PaymentPlan, SalaryPayment

User = get_user_model()


# ============================================================================
# NOTIFICATION UTILITIES
# ============================================================================

def create_notification(recipient, message, notification_type='general'):
    """
    Create a notification for a user.
    
    Args:
        recipient: User instance or user ID
        message: Notification message text
        notification_type: Type of notification (default: 'general')
    
    Returns:
        Notification instance
    
    Example:
        >>> user = User.objects.get(email='student@example.com')
        >>> create_notification(user, "Your payment was recorded", 'payment')
    """
    if isinstance(recipient, (str, int)):
        try:
            recipient = User.objects.get(id=recipient)
        except User.DoesNotExist:
            return None
    
    if not isinstance(recipient, User):
        return None
    
    return Notification.objects.create(
        recipient=recipient,
        message=message,
        type=notification_type
    )


def notify_all_admins(message, notification_type='general'):
    """
    Send notification to all admin users.
    
    Args:
        message: Notification message
        notification_type: Type of notification (default: 'general')
    
    Returns:
        List of created notifications
    
    Example:
        >>> notify_all_admins("New expense submitted: Internet Bill", 'expense')
    """
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    notifications = []
    
    for admin in admins:
        notification = create_notification(admin, message, notification_type)
        if notification:
            notifications.append(notification)
    
    return notifications


def notify_cohort_students(cohort, message, notification_type='cohort'):
    """
    Send notification to all students in a cohort.
    
    Args:
        cohort: Cohort instance
        message: Notification message
        notification_type: Type of notification (default: 'cohort')
    
    Returns:
        List of created notifications
    
    Example:
        >>> cohort = Cohort.objects.get(name='Cohort A')
        >>> notify_cohort_students(cohort, "New assignment posted", 'general')
    """
    notifications = []
    
    for student in cohort.students.all():
        notification = create_notification(student, message, notification_type)
        if notification:
            notifications.append(notification)
    
    return notifications


def notify_staff_members(message, notification_type='general', exclude_user=None):
    """
    Send notification to all staff members.
    
    Args:
        message: Notification message
        notification_type: Type of notification (default: 'general')
        exclude_user: User to exclude from notifications (optional)
    
    Returns:
        List of created notifications
    """
    staff = User.objects.filter(is_staff=True)
    
    if exclude_user:
        staff = staff.exclude(id=exclude_user.id)
    
    notifications = []
    for staff_member in staff:
        notification = create_notification(staff_member, message, notification_type)
        if notification:
            notifications.append(notification)
    
    return notifications


# ============================================================================
# PAYMENT UTILITIES
# ============================================================================

def calculate_student_balance(student):
    """
    Calculate total balance for a student across all payment plans.
    
    Args:
        student: User instance (student)
    
    Returns:
        Dictionary with payment summary
    
    Example:
        >>> student = User.objects.get(email='student@example.com')
        >>> calculate_student_balance(student)
        {
            'total_due': Decimal('300000.00'),
            'total_paid': Decimal('150000.00'),
            'total_remaining': Decimal('150000.00'),
            'plan_count': 1
        }
    """
    plans = PaymentPlan.objects.filter(student=student)
    
    summary = plans.aggregate(
        total_due=Sum('amount_total'),
        total_paid=Sum('amount_paid'),
        plan_count=Count('id')
    )
    
    total_due = summary['total_due'] or Decimal('0.00')
    total_paid = summary['total_paid'] or Decimal('0.00')
    
    return {
        'total_due': total_due,
        'total_paid': total_paid,
        'total_remaining': total_due - total_paid,
        'plan_count': summary['plan_count'] or 0
    }


def get_overdue_payment_plans():
    """
    Get all payment plans that are overdue.
    A plan is overdue if it's not complete and the cohort has ended.
    
    Returns:
        QuerySet of overdue PaymentPlan objects
    """
    today = timezone.now().date()
    
    return PaymentPlan.objects.filter(
        status__in=['pending', 'partial'],
        cohort__end_date__lt=today
    ).select_related('student', 'course', 'cohort')


# ============================================================================
# EXPENSE UTILITIES
# ============================================================================

def calculate_expense_summary(start_date=None, end_date=None, status=None, category=None):
    """
    Calculate expense summary with optional filters.
    
    Args:
        start_date: Filter expenses from this date
        end_date: Filter expenses to this date
        status: Filter by status
        category: Filter by category
    
    Returns:
        Dictionary with expense summary
    
    Example:
        >>> from datetime import date
        >>> summary = calculate_expense_summary(
        ...     start_date=date(2025, 1, 1),
        ...     end_date=date(2025, 1, 31),
        ...     status='paid'
        ... )
    """
    expenses = OfficeExpense.objects.all()
    
    # Apply filters
    if start_date:
        expenses = expenses.filter(expense_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(expense_date__lte=end_date)
    if status:
        expenses = expenses.filter(status=status)
    if category:
        expenses = expenses.filter(category=category)
    
    # Calculate totals by status
    summary = {
        'total_expenses': expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'total_count': expenses.count(),
    }
    
    # Breakdown by status
    for status_choice in ['pending', 'approved', 'paid', 'rejected']:
        status_expenses = expenses.filter(status=status_choice)
        summary[f'{status_choice}_count'] = status_expenses.count()
        summary[f'{status_choice}_amount'] = status_expenses.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
    
    # Breakdown by category
    summary['by_category'] = {}
    for expense_category in OfficeExpense.CATEGORY_CHOICES:
        cat_code = expense_category[0]
        cat_expenses = expenses.filter(category=cat_code)
        cat_total = cat_expenses.aggregate(total=Sum('amount'))['total']
        if cat_total:
            summary['by_category'][cat_code] = {
                'amount': cat_total,
                'count': cat_expenses.count()
            }
    
    return summary


def get_pending_expenses_for_approval():
    """
    Get all pending expenses that need approval.
    
    Returns:
        QuerySet of pending OfficeExpense objects
    """
    return OfficeExpense.objects.filter(
        status='pending'
    ).select_related('submitted_by').order_by('-expense_date')


# ============================================================================
# SALARY UTILITIES
# ============================================================================

def calculate_staff_salary_summary(staff):
    """
    Calculate salary summary for a staff member.
    
    Args:
        staff: User instance (staff member)
    
    Returns:
        Dictionary with salary summary
    """
    salaries = SalaryPayment.objects.filter(staff=staff)
    
    summary = salaries.aggregate(
        total_due=Sum('amount_due'),
        total_paid=Sum('amount_paid'),
        payment_count=Count('id')
    )
    
    total_due = summary['total_due'] or Decimal('0.00')
    total_paid = summary['total_paid'] or Decimal('0.00')
    
    return {
        'total_due': total_due,
        'total_paid': total_paid,
        'total_remaining': total_due - total_paid,
        'payment_count': summary['payment_count'] or 0,
        'pending_count': salaries.filter(status='pending').count(),
        'complete_count': salaries.filter(status='complete').count(),
    }


def get_pending_salary_payments():
    """
    Get all salary payments that are pending or partial.
    
    Returns:
        QuerySet of pending/partial SalaryPayment objects
    """
    return SalaryPayment.objects.filter(
        status__in=['pending', 'partial']
    ).select_related('staff', 'paid_by').order_by('-payment_date')


# ============================================================================
# GENERAL UTILITIES
# ============================================================================

def format_currency(amount):
    """
    Format amount as Nigerian Naira currency.
    
    Args:
        amount: Decimal or float amount
    
    Returns:
        Formatted string
    
    Example:
        >>> format_currency(150000)
        '₦150,000.00'
    """
    if amount is None:
        return '₦0.00'
    
    try:
        amount = Decimal(str(amount))
        return f'₦{amount:,.2f}'
    except (ValueError, TypeError):
        return '₦0.00'


def get_date_range_filter(period='this_month'):
    """
    Get date range for common periods.
    
    Args:
        period: 'today', 'this_week', 'this_month', 'this_year'
    
    Returns:
        Tuple of (start_date, end_date)
    
    Example:
        >>> start, end = get_date_range_filter('this_month')
    """
    today = timezone.now().date()
    
    if period == 'today':
        return today, today
    
    elif period == 'this_week':
        start = today - timezone.timedelta(days=today.weekday())
        end = start + timezone.timedelta(days=6)
        return start, end
    
    elif period == 'this_month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(day=31)
        else:
            end = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
        return start, end
    
    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
    
    return None, None


def search_users(query, user_type=None):
    """
    Search users by name or email.
    
    Args:
        query: Search query string
        user_type: Filter by user type ('student', 'staff', 'admin')
    
    Returns:
        QuerySet of User objects
    
    Example:
        >>> users = search_users('john', user_type='student')
    """
    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )
    
    if user_type == 'student':
        users = users.filter(is_student=True)
    elif user_type == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif user_type == 'admin':
        users = users.filter(is_staff=True, is_superuser=True)
    
    return users.distinct()


def bulk_create_notifications(user_list, message, notification_type='general'):
    """
    Efficiently create notifications for multiple users.
    
    Args:
        user_list: List of User instances or IDs
        message: Notification message
        notification_type: Type of notification
    
    Returns:
        Number of notifications created
    
    Example:
        >>> students = User.objects.filter(is_student=True)
        >>> bulk_create_notifications(students, "System maintenance tonight", 'general')
    """
    notifications = []
    
    for user in user_list:
        if isinstance(user, (str, int)):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                continue
        
        notifications.append(
            Notification(
                recipient=user,
                message=message,
                type=notification_type
            )
        )
    
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    return len(notifications)