from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Course(models.Model):
    """Course model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField(help_text="Duration in weeks")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='courses_created',
        limit_choices_to={'is_staff': True}  # Changed to use is_staff
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Cohort(models.Model):
    """Cohort model for grouping students"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cohorts')
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cohorts_teaching',
        limit_choices_to={'is_staff': True}  # Instructors are staff
    )
    students = models.ManyToManyField(
        User,
        related_name='cohorts_enrolled',
        blank=True,
        limit_choices_to={'is_student': True}  # Changed to use is_student
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cohorts'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.course.title}"


class PaymentPlan(models.Model):
    """Payment plan for students"""
    PLAN_TYPE_CHOICES = [
        ('full', 'Full Payment'),
        ('50/50', '50/50 Split'),
        ('installment', 'Installment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
        ('overdue', 'Overdue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_plans',
        limit_choices_to={'is_student': True}  # Changed to use is_student
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payment_plans')
    cohort = models.ForeignKey(
        Cohort, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payment_plans'
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.plan_type}"

    @property
    def amount_remaining(self):
        return self.amount_total - self.amount_paid

    @property
    def payment_percentage(self):
        if self.amount_total == 0:
            return 0
        return (self.amount_paid / self.amount_total) * 100

    def update_status(self):
        """Auto-update status based on payment"""
        if self.amount_paid >= self.amount_total:
            self.status = 'complete'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save()


class PaymentLog(models.Model):
    """Individual payment records"""
    PAYMENT_METHOD_CHOICES = [
        ('transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name='payment_logs'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        limit_choices_to={'is_student': True}  # Changed to use is_student
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    receipt_url = models.URLField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_recorded',
        limit_choices_to={'is_staff': True}  # Changed to use is_staff (admin)
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_logs'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student.get_full_name()} - ₦{self.amount}"


class SalaryPayment(models.Model):
    """Salary payment records for staff"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='salary_payments',
        limit_choices_to={'is_staff': True}  # Staff who aren't admins
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='salaries_paid',
        limit_choices_to={'is_staff': True, 'is_superuser': True}  # Only superuser admins
    )
    payment_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.staff.get_full_name()} - ₦{self.amount_paid}"

    @property
    def amount_remaining(self):
        return self.amount_due - self.amount_paid


class OfficeExpense(models.Model):
    """Office expense tracking"""
    CATEGORY_CHOICES = [
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('internet', 'Internet'),
        ('equipment', 'Equipment'),
        ('supplies', 'Office Supplies'),
        ('maintenance', 'Maintenance'),
        ('transportation', 'Transportation'),
        ('marketing', 'Marketing'),
        ('software', 'Software/Subscriptions'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('cheque', 'Cheque'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Brief description of expense")
    description = models.TextField(blank=True, help_text="Detailed description")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(help_text="Date when expense was incurred")
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True
    )
    receipt_url = models.URLField(blank=True, null=True, help_text="URL to receipt/invoice")
    
    # User tracking - all staff can submit/approve
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses_submitted',
        help_text="Staff/Admin who submitted the expense"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses_approved',
        limit_choices_to={'is_staff': True},  # Changed to use is_staff
        help_text="Admin who approved the expense"
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses_paid',
        limit_choices_to={'is_staff': True},  # Changed to use is_staff
        help_text="Admin who processed the payment"
    )
    
    # Notes and dates
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'office_expenses'
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['status', 'expense_date']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} - ₦{self.amount} ({self.category})"

    def approve(self, admin_user):
        """Approve the expense"""
        self.status = 'approved'
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()

    def reject(self, admin_user, reason):
        """Reject the expense"""
        self.status = 'rejected'
        self.approved_by = admin_user
        self.rejection_reason = reason
        self.approved_at = timezone.now()
        self.save()

    def mark_as_paid(self, admin_user, payment_method):
        """Mark expense as paid"""
        self.status = 'paid'
        self.paid_by = admin_user
        self.payment_method = payment_method
        self.paid_at = timezone.now()
        self.save()


class Notification(models.Model):
    """Notification model for real-time alerts"""
    TYPE_CHOICES = [
        ('verification', 'Verification'),
        ('role_assignment', 'Role Assignment'),
        ('payment', 'Payment'),
        ('salary', 'Salary'),
        ('cohort', 'Cohort'),
        ('expense', 'Expense'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.type} - {self.recipient.email}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()