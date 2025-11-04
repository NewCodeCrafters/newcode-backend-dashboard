from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import (
    Course, Cohort, PaymentPlan, PaymentLog,
    SalaryPayment, OfficeExpense, Notification
)

User = get_user_model()


# ============================================================================
# USER SERIALIZERS (Nested/Reference)
# ============================================================================

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested relationships"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'email', 'full_name']


# ============================================================================
# COURSE SERIALIZERS
# ============================================================================

class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing courses"""
    created_by = UserBasicSerializer(read_only=True)
    cohort_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'duration_weeks',
            'created_by', 'cohort_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_cohort_count(self, obj):
        return obj.cohorts.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course details with related cohorts"""
    created_by = UserBasicSerializer(read_only=True)
    cohorts = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'duration_weeks',
            'created_by', 'cohorts', 'total_students',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_cohorts(self, obj):
        cohorts = obj.cohorts.all()[:5]  # Limit to 5 most recent
        return CohortListSerializer(cohorts, many=True).data
    
    def get_total_students(self, obj):
        # Count unique students across all cohorts
        return User.objects.filter(
            cohorts_enrolled__course=obj
        ).distinct().count()


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'duration_weeks']
    
    def validate_duration_weeks(self, value):
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 week.")
        if value > 52:
            raise serializers.ValidationError("Duration cannot exceed 52 weeks.")
        return value
    
    def create(self, validated_data):
        # Add the current user as creator
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# ============================================================================
# COHORT SERIALIZERS
# ============================================================================

class CohortListSerializer(serializers.ModelSerializer):
    """Serializer for listing cohorts"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor = UserBasicSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cohort
        fields = [
            'id', 'name', 'course', 'course_title', 'instructor',
            'student_count', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.students.count()


class CohortDetailSerializer(serializers.ModelSerializer):
    """Serializer for cohort details with students list"""
    course = CourseListSerializer(read_only=True)
    instructor = UserBasicSerializer(read_only=True)
    students = UserBasicSerializer(many=True, read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Cohort
        fields = [
            'id', 'name', 'course', 'instructor', 'students',
            'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_active(self, obj):
        today = timezone.now().date()
        return obj.start_date <= today <= obj.end_date


class CohortCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating cohorts"""
    
    class Meta:
        model = Cohort
        fields = [
            'name', 'course', 'instructor',
            'start_date', 'end_date'
        ]
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        
        # Validate instructor is staff
        if data.get('instructor') and not data['instructor'].is_staff:
            raise serializers.ValidationError({
                'instructor': 'Instructor must be a staff member.'
            })
        
        return data


class CohortAssignStudentsSerializer(serializers.Serializer):
    """Serializer for assigning students to cohort"""
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )
    
    def validate_student_ids(self, value):
        # Check all users exist and are students
        students = User.objects.filter(id__in=value)
        
        if students.count() != len(value):
            raise serializers.ValidationError("Some student IDs are invalid.")
        
        non_students = students.exclude(is_student=True)
        if non_students.exists():
            raise serializers.ValidationError(
                f"Users with IDs {list(non_students.values_list('id', flat=True))} are not students."
            )
        
        return value


# ============================================================================
# PAYMENT PLAN SERIALIZERS
# ============================================================================

class PaymentPlanListSerializer(serializers.ModelSerializer):
    """Serializer for listing payment plans"""
    student = UserBasicSerializer(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    cohort_name = serializers.CharField(source='cohort.name', read_only=True, allow_null=True)
    amount_remaining = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    payment_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'student', 'course', 'course_title', 'cohort', 'cohort_name',
            'plan_type', 'amount_total', 'amount_paid', 'amount_remaining',
            'payment_percentage', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'amount_paid', 'status', 'created_at', 'updated_at']


class PaymentPlanDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment plan details with payment logs"""
    student = UserBasicSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    cohort = CohortListSerializer(read_only=True)
    amount_remaining = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    payment_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    payment_logs = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'student', 'course', 'cohort', 'plan_type',
            'amount_total', 'amount_paid', 'amount_remaining',
            'payment_percentage', 'status', 'payment_logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'amount_paid', 'status', 'created_at', 'updated_at']
    
    def get_payment_logs(self, obj):
        logs = obj.payment_logs.all()[:10]  # Last 10 payments
        return PaymentLogListSerializer(logs, many=True).data


class PaymentPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment plans"""
    
    class Meta:
        model = PaymentPlan
        fields = [
            'student', 'course', 'cohort', 'plan_type', 'amount_total'
        ]
    
    def validate_student(self, value):
        if not value.is_student:
            raise serializers.ValidationError("Selected user is not a student.")
        return value
    
    def validate_amount_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate(self, data):
        # Check if student already has a payment plan for this course
        student = data.get('student')
        course = data.get('course')
        
        if student and course:
            existing = PaymentPlan.objects.filter(
                student=student,
                course=course
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    "Student already has a payment plan for this course."
                )
        
        return data


class PaymentPlanUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment plans"""
    
    class Meta:
        model = PaymentPlan
        fields = ['amount_total', 'status']
    
    def validate_amount_total(self, value):
        if value < self.instance.amount_paid:
            raise serializers.ValidationError(
                f"Amount total cannot be less than amount already paid (₦{self.instance.amount_paid})."
            )
        return value


# ============================================================================
# PAYMENT LOG SERIALIZERS
# ============================================================================

class PaymentLogListSerializer(serializers.ModelSerializer):
    """Serializer for listing payment logs"""
    student = UserBasicSerializer(read_only=True)
    recorded_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PaymentLog
        fields = [
            'id', 'payment_plan', 'student', 'amount', 'payment_method',
            'receipt_url', 'payment_date', 'recorded_by', 'notes'
        ]
        read_only_fields = ['id', 'payment_date']


class PaymentLogDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment log details"""
    student = UserBasicSerializer(read_only=True)
    payment_plan = PaymentPlanListSerializer(read_only=True)
    recorded_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PaymentLog
        fields = [
            'id', 'payment_plan', 'student', 'amount', 'payment_method',
            'receipt_url', 'payment_date', 'recorded_by', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'payment_date', 'created_at']


class PaymentLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment logs"""
    
    class Meta:
        model = PaymentLog
        fields = [
            'payment_plan', 'student', 'amount',
            'payment_method', 'receipt_url', 'notes'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate(self, data):
        payment_plan = data.get('payment_plan')
        student = data.get('student')
        amount = data.get('amount')
        
        # Verify student matches payment plan
        if payment_plan and student:
            if payment_plan.student != student:
                raise serializers.ValidationError({
                    'student': 'Student does not match payment plan.'
                })
        
        # Check if payment exceeds remaining balance
        if payment_plan and amount:
            remaining = payment_plan.amount_remaining
            if amount > remaining:
                raise serializers.ValidationError({
                    'amount': f'Payment amount (₦{amount}) exceeds remaining balance (₦{remaining}).'
                })
        
        return data
    
    def create(self, validated_data):
        # Add the current user as recorder
        validated_data['recorded_by'] = self.context['request'].user
        
        # Create payment log
        payment_log = super().create(validated_data)
        
        # Update payment plan
        payment_plan = payment_log.payment_plan
        payment_plan.amount_paid += payment_log.amount
        payment_plan.update_status()
        
        return payment_log


# ============================================================================
# SALARY PAYMENT SERIALIZERS
# ============================================================================

class SalaryPaymentListSerializer(serializers.ModelSerializer):
    """Serializer for listing salary payments"""
    staff = UserBasicSerializer(read_only=True)
    paid_by = UserBasicSerializer(read_only=True)
    amount_remaining = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = SalaryPayment
        fields = [
            'id', 'staff', 'amount_due', 'amount_paid', 'amount_remaining',
            'status', 'paid_by', 'payment_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalaryPaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for salary payment details"""
    staff = UserBasicSerializer(read_only=True)
    paid_by = UserBasicSerializer(read_only=True)
    amount_remaining = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = SalaryPayment
        fields = [
            'id', 'staff', 'amount_due', 'amount_paid', 'amount_remaining',
            'status', 'paid_by', 'payment_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalaryPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating salary payments"""
    
    class Meta:
        model = SalaryPayment
        fields = [
            'staff', 'amount_due', 'amount_paid', 'payment_date', 'notes'
        ]
    
    def validate_staff(self, value):
        if not value.is_staff:
            raise serializers.ValidationError("Selected user is not a staff member.")
        return value
    
    def validate_amount_due(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount due must be greater than zero.")
        return value
    
    def validate_amount_paid(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount paid cannot be negative.")
        return value
    
    def validate(self, data):
        amount_due = data.get('amount_due')
        amount_paid = data.get('amount_paid')
        
        if amount_paid > amount_due:
            raise serializers.ValidationError({
                'amount_paid': 'Amount paid cannot exceed amount due.'
            })
        
        return data
    
    def create(self, validated_data):
        # Add the current user as payer
        validated_data['paid_by'] = self.context['request'].user
        
        # Set status based on payment
        amount_due = validated_data['amount_due']
        amount_paid = validated_data['amount_paid']
        
        if amount_paid >= amount_due:
            validated_data['status'] = 'complete'
        elif amount_paid > 0:
            validated_data['status'] = 'partial'
        else:
            validated_data['status'] = 'pending'
        
        return super().create(validated_data)


class SalaryPaymentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating salary payments"""
    
    class Meta:
        model = SalaryPayment
        fields = ['amount_paid', 'payment_date', 'notes']
    
    def validate_amount_paid(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount paid cannot be negative.")
        if value > self.instance.amount_due:
            raise serializers.ValidationError(
                f"Amount paid cannot exceed amount due (₦{self.instance.amount_due})."
            )
        return value
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        
        # Update status
        if instance.amount_paid >= instance.amount_due:
            instance.status = 'complete'
        elif instance.amount_paid > 0:
            instance.status = 'partial'
        else:
            instance.status = 'pending'
        
        instance.save()
        return instance


# ============================================================================
# OFFICE EXPENSE SERIALIZERS
# ============================================================================

class OfficeExpenseListSerializer(serializers.ModelSerializer):
    """Serializer for listing office expenses"""
    submitted_by = UserBasicSerializer(read_only=True)
    approved_by = UserBasicSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OfficeExpense
        fields = [
            'id', 'title', 'category', 'category_display', 'amount',
            'expense_date', 'status', 'status_display', 'submitted_by',
            'approved_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OfficeExpenseDetailSerializer(serializers.ModelSerializer):
    """Serializer for office expense details"""
    submitted_by = UserBasicSerializer(read_only=True)
    approved_by = UserBasicSerializer(read_only=True)
    paid_by = UserBasicSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OfficeExpense
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'amount', 'expense_date', 'status', 'status_display',
            'payment_method', 'receipt_url', 'submitted_by', 'approved_by',
            'paid_by', 'notes', 'rejection_reason', 'approved_at', 'paid_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'submitted_by', 'approved_by', 'paid_by',
            'approved_at', 'paid_at', 'created_at', 'updated_at'
        ]


class OfficeExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating office expenses"""
    
    class Meta:
        model = OfficeExpense
        fields = [
            'title', 'description', 'category', 'amount',
            'expense_date', 'receipt_url', 'notes'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_expense_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value
    
    def create(self, validated_data):
        # Add the current user as submitter
        validated_data['submitted_by'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class OfficeExpenseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating office expenses (only pending ones)"""
    
    class Meta:
        model = OfficeExpense
        fields = ['title', 'description', 'amount', 'category', 'receipt_url', 'notes']
    
    def validate(self, data):
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                "Only pending expenses can be updated."
            )
        return data


class OfficeExpenseApproveSerializer(serializers.Serializer):
    """Serializer for approving expenses"""
    notes = serializers.CharField(required=False, allow_blank=True)


class OfficeExpenseRejectSerializer(serializers.Serializer):
    """Serializer for rejecting expenses"""
    rejection_reason = serializers.CharField(required=True)
    
    def validate_rejection_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason is required.")
        return value


class OfficeExpenseMarkPaidSerializer(serializers.Serializer):
    """Serializer for marking expenses as paid"""
    payment_method = serializers.ChoiceField(
        choices=OfficeExpense.PAYMENT_METHOD_CHOICES
    )
    notes = serializers.CharField(required=False, allow_blank=True)


# ============================================================================
# NOTIFICATION SERIALIZERS
# ============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'message', 'type', 'type_display',
            'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'message', 'type', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications (admin use)"""
    
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'type']
    
    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value