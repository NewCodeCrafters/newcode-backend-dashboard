"""
API ViewSets for NewCodeCrafters Management System.
Handles all CRUD operations and custom actions for courses, cohorts, payments, etc.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.contrib.auth import get_user_model

from .models import Course, Cohort, PaymentPlan, PaymentLog, SalaryPayment, OfficeExpense, Notification
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer,
    CohortListSerializer, CohortDetailSerializer, CohortCreateUpdateSerializer, CohortAssignStudentsSerializer,
    PaymentPlanListSerializer, PaymentPlanDetailSerializer, PaymentPlanCreateSerializer, PaymentPlanUpdateSerializer,
    PaymentLogListSerializer, PaymentLogDetailSerializer, PaymentLogCreateSerializer,
    SalaryPaymentListSerializer, SalaryPaymentDetailSerializer, SalaryPaymentCreateSerializer, SalaryPaymentUpdateSerializer,
    OfficeExpenseListSerializer, OfficeExpenseDetailSerializer, OfficeExpenseCreateSerializer, OfficeExpenseUpdateSerializer,
    OfficeExpenseApproveSerializer, OfficeExpenseRejectSerializer, OfficeExpenseMarkPaidSerializer,
    NotificationSerializer, NotificationCreateSerializer,
)
from .permissions import IsAdminUser, IsStaffUser, IsOwnerOrAdmin, IsOwnerOrStaff, CanManageExpenses
from .utils import (
    create_notification, notify_all_admins, notify_cohort_students,
    calculate_expense_summary, get_pending_expenses_for_approval
)

User = get_user_model()


# ============================================================================
# COURSE VIEWSET
# ============================================================================

@extend_schema(tags=['Courses'])
class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses.
    
    Permissions:
    - List/Retrieve: Authenticated users
    - Create/Update/Delete: Staff users only
    
    Endpoints:
    - GET /api/courses/ - List all courses
    - POST /api/courses/ - Create new course
    - GET /api/courses/{id}/ - Get course details
    - PATCH /api/courses/{id}/ - Update course
    - DELETE /api/courses/{id}/ - Delete course
    """
    queryset = Course.objects.all().select_related('created_by').prefetch_related('cohorts')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['duration_weeks', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'duration_weeks']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStaffUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return CourseListSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        else:
            return CourseCreateUpdateSerializer
    
    @extend_schema(
        summary="List all courses",
        description="Get a paginated list of all courses with optional filtering and search.",
        responses={200: CourseListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all courses."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new course",
        description="Create a new course. Only staff members can create courses.",
        request=CourseCreateUpdateSerializer,
        responses={
            201: CourseDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new course."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        
        # Notify admins
        notify_all_admins(
            f"New course created: {course.title} by {request.user.get_full_name()}",
            'general'
        )
        
        return Response(
            CourseDetailSerializer(course).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get course details",
        description="Retrieve detailed information about a specific course.",
        responses={200: CourseDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get course details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update a course",
        description="Update course details. Only staff members can update courses.",
        request=CourseCreateUpdateSerializer,
        responses={
            200: CourseDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a course."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update a course",
        description="Partially update course details. Only staff members can update courses.",
        request=CourseCreateUpdateSerializer,
        responses={200: CourseDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a course."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete a course",
        description="Delete a course. Only staff members can delete courses.",
        responses={
            204: OpenApiResponse(description="Course deleted successfully"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a course."""
        course = self.get_object()
        course_title = course.title
        
        response = super().destroy(request, *args, **kwargs)
        
        # Notify admins
        notify_all_admins(
            f"Course deleted: {course_title} by {request.user.get_full_name()}",
            'general'
        )
        
        return response


# ============================================================================
# COHORT VIEWSET
# ============================================================================

@extend_schema(tags=['Cohorts'])
class CohortViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cohorts.
    
    Permissions:
    - List/Retrieve: Authenticated users
    - Create/Update/Delete: Staff users only
    - Assign Students: Staff users only
    
    Endpoints:
    - GET /api/cohorts/ - List all cohorts
    - POST /api/cohorts/ - Create new cohort
    - GET /api/cohorts/{id}/ - Get cohort details
    - PATCH /api/cohorts/{id}/ - Update cohort
    - DELETE /api/cohorts/{id}/ - Delete cohort
    - PATCH /api/cohorts/{id}/assign-students/ - Assign students to cohort
    """
    queryset = Cohort.objects.all().select_related('course', 'instructor').prefetch_related('students')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'instructor', 'start_date', 'end_date']
    search_fields = ['name', 'course__title']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStaffUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return CohortListSerializer
        elif self.action == 'retrieve':
            return CohortDetailSerializer
        elif self.action == 'assign_students':
            return CohortAssignStudentsSerializer
        else:
            return CohortCreateUpdateSerializer
    
    @extend_schema(
        summary="List all cohorts",
        description="Get a paginated list of all cohorts with optional filtering.",
        responses={200: CohortListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all cohorts."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new cohort",
        description="Create a new cohort. Only staff members can create cohorts.",
        request=CohortCreateUpdateSerializer,
        responses={
            201: CohortDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new cohort."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cohort = serializer.save()
        
        return Response(
            CohortDetailSerializer(cohort).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get cohort details",
        description="Retrieve detailed information about a specific cohort including enrolled students.",
        responses={200: CohortDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get cohort details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update a cohort",
        description="Update cohort details. Only staff members can update cohorts.",
        request=CohortCreateUpdateSerializer,
        responses={200: CohortDetailSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update a cohort."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update a cohort",
        description="Partially update cohort details. Only staff members can update cohorts.",
        request=CohortCreateUpdateSerializer,
        responses={200: CohortDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a cohort."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete a cohort",
        description="Delete a cohort. Only staff members can delete cohorts.",
        responses={204: OpenApiResponse(description="Cohort deleted successfully")}
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a cohort."""
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Assign students to cohort",
        description="Add multiple students to a cohort. Only staff members can assign students.",
        request=CohortAssignStudentsSerializer,
        responses={
            200: CohortDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    @action(detail=True, methods=['patch'], url_path='assign-students')
    def assign_students(self, request, pk=None):
        """
        Assign students to a cohort.
        
        Request body:
        {
            "student_ids": ["uuid1", "uuid2", "uuid3"]
        }
        """
        cohort = self.get_object()
        serializer = CohortAssignStudentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_ids = serializer.validated_data['student_ids']
        students = User.objects.filter(id__in=student_ids, is_student=True)
        
        # Add students to cohort
        cohort.students.add(*students)
        
        # Notify each student
        for student in students:
            create_notification(
                recipient=student,
                message=f"You have been enrolled in {cohort.name} - {cohort.course.title}",
                notification_type='cohort'
            )
        
        return Response(
            CohortDetailSerializer(cohort).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Remove students from cohort",
        description="Remove students from a cohort. Only staff members can remove students.",
        request=CohortAssignStudentsSerializer,
        responses={200: CohortDetailSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='remove-students')
    def remove_students(self, request, pk=None):
        """
        Remove students from a cohort.
        
        Request body:
        {
            "student_ids": ["uuid1", "uuid2"]
        }
        """
        cohort = self.get_object()
        serializer = CohortAssignStudentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_ids = serializer.validated_data['student_ids']
        students = User.objects.filter(id__in=student_ids)
        
        # Remove students from cohort
        cohort.students.remove(*students)
        
        # Notify each student
        for student in students:
            create_notification(
                recipient=student,
                message=f"You have been removed from {cohort.name} - {cohort.course.title}",
                notification_type='cohort'
            )
        
        return Response(
            CohortDetailSerializer(cohort).data,
            status=status.HTTP_200_OK
        )

# ============================================================================
# PAYMENT PLAN VIEWSET
# ============================================================================

@extend_schema(tags=['Payment Plans'])
class PaymentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment plans.
    
    Permissions:
    - List/Retrieve: Admin (all) or Student (own only)
    - Create/Update/Delete: Admin only
    
    Endpoints:
    - GET /api/payments/plans/ - List payment plans
    - POST /api/payments/plans/ - Create new payment plan
    - GET /api/payments/plans/{id}/ - Get payment plan details
    - PATCH /api/payments/plans/{id}/ - Update payment plan
    - DELETE /api/payments/plans/{id}/ - Delete payment plan
    """
    queryset = PaymentPlan.objects.all().select_related(
        'student', 'course', 'cohort'
    ).prefetch_related('payment_logs')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'cohort', 'plan_type', 'status']
    search_fields = ['student__email', 'student__first_name', 'student__last_name', 'course__title']
    ordering_fields = ['created_at', 'amount_total', 'amount_paid', 'status']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        Students can only see their own payment plans.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff and user.is_superuser:
            # Admins see everything
            return queryset
        elif user.is_student:
            # Students see only their own
            return queryset.filter(student=user)
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PaymentPlanListSerializer
        elif self.action == 'retrieve':
            return PaymentPlanDetailSerializer
        elif self.action == 'create':
            return PaymentPlanCreateSerializer
        else:
            return PaymentPlanUpdateSerializer
    
    @extend_schema(
        summary="List payment plans",
        description="Get a paginated list of payment plans. Students see only their own.",
        responses={200: PaymentPlanListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List payment plans."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a payment plan",
        description="Create a new payment plan for a student. Admin only.",
        request=PaymentPlanCreateSerializer,
        responses={
            201: PaymentPlanDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new payment plan."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_plan = serializer.save()
        
        # Notify student
        create_notification(
            recipient=payment_plan.student,
            message=f"Payment plan created for {payment_plan.course.title}: ₦{payment_plan.amount_total:,.2f} ({payment_plan.get_plan_type_display()})",
            notification_type='payment'
        )
        
        return Response(
            PaymentPlanDetailSerializer(payment_plan).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get payment plan details",
        description="Retrieve detailed information about a specific payment plan.",
        responses={200: PaymentPlanDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get payment plan details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update a payment plan",
        description="Update payment plan details. Admin only.",
        request=PaymentPlanUpdateSerializer,
        responses={200: PaymentPlanDetailSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update a payment plan."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update a payment plan",
        description="Partially update payment plan details. Admin only.",
        request=PaymentPlanUpdateSerializer,
        responses={200: PaymentPlanDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a payment plan."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete a payment plan",
        description="Delete a payment plan. Admin only.",
        responses={204: OpenApiResponse(description="Payment plan deleted")}
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a payment plan."""
        return super().destroy(request, *args, **kwargs)


# ============================================================================
# PAYMENT LOG VIEWSET
# ============================================================================

@extend_schema(tags=['Payment Logs'])
class PaymentLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment logs.
    
    Permissions:
    - List/Retrieve: Staff (all) or Student (own only)
    - Create: Staff only
    - Update/Delete: Not allowed
    
    Endpoints:
    - GET /api/payments/logs/ - List payment logs
    - POST /api/payments/logs/ - Record a new payment
    - GET /api/payments/logs/{id}/ - Get payment log details
    
    Query Parameters:
    - student_id: Filter by student UUID
    - payment_plan: Filter by payment plan UUID
    - payment_method: Filter by payment method
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    """
    queryset = PaymentLog.objects.all().select_related(
        'student', 'payment_plan', 'recorded_by'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'payment_plan', 'payment_method']
    search_fields = ['student__email', 'student__first_name', 'student__last_name', 'notes']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT, PATCH, DELETE
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsStaffUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user role and query parameters.
        Students can only see their own payment logs.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Role-based filtering
        if user.is_staff:
            # Staff see everything
            pass
        elif user.is_student:
            # Students see only their own
            queryset = queryset.filter(student=user)
        else:
            return queryset.none()
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        # Student ID filtering (for staff)
        student_id = self.request.query_params.get('student_id')
        if student_id and user.is_staff:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PaymentLogListSerializer
        elif self.action == 'retrieve':
            return PaymentLogDetailSerializer
        else:
            return PaymentLogCreateSerializer
    
    @extend_schema(
        summary="List payment logs",
        description="Get a paginated list of payment logs. Students see only their own.",
        parameters=[
            OpenApiParameter(name='student_id', type=str, description='Filter by student UUID'),
            OpenApiParameter(name='payment_plan', type=str, description='Filter by payment plan UUID'),
            OpenApiParameter(name='start_date', type=str, description='Filter from date (YYYY-MM-DD)'),
            OpenApiParameter(name='end_date', type=str, description='Filter to date (YYYY-MM-DD)'),
        ],
        responses={200: PaymentLogListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List payment logs."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Record a payment",
        description="Record a new payment for a student. Staff only. Automatically updates payment plan.",
        request=PaymentLogCreateSerializer,
        responses={
            201: PaymentLogDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Record a new payment.
        Automatically updates the payment plan's amount_paid and status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_log = serializer.save()
        
        # Notify student
        create_notification(
            recipient=payment_log.student,
            message=f"Payment of ₦{payment_log.amount:,.2f} recorded for {payment_log.payment_plan.course.title}. Remaining balance: ₦{payment_log.payment_plan.amount_remaining:,.2f}",
            notification_type='payment'
        )
        
        return Response(
            PaymentLogDetailSerializer(payment_log).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get payment log details",
        description="Retrieve detailed information about a specific payment log.",
        responses={200: PaymentLogDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get payment log details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get student payment summary",
        description="Get payment summary for a specific student. Staff only.",
        responses={
            200: OpenApiResponse(
                description="Payment summary",
                response={
                    'type': 'object',
                    'properties': {
                        'total_due': {'type': 'string'},
                        'total_paid': {'type': 'string'},
                        'total_remaining': {'type': 'string'},
                        'plan_count': {'type': 'integer'}
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='student-summary/(?P<student_id>[^/.]+)')
    def student_summary(self, request, student_id=None):
        """
        Get payment summary for a student.
        
        URL: /api/payments/logs/student-summary/{student_id}/
        """
        try:
            student = User.objects.get(id=student_id, is_student=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summary = calculate_student_balance(student)
        
        return Response({
            'student': {
                'id': str(student.id),
                'email': student.email,
                'full_name': student.get_full_name()
            },
            'total_due': str(summary['total_due']),
            'total_paid': str(summary['total_paid']),
            'total_remaining': str(summary['total_remaining']),
            'plan_count': summary['plan_count']
        })


# ============================================================================
# SALARY PAYMENT VIEWSET
# ============================================================================

@extend_schema(tags=['Salary Payments'])
class SalaryPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing salary payments.
    
    Permissions:
    - List/Retrieve: Admin (all) or Staff (own only)
    - Create/Update: Admin only
    - Delete: Not allowed
    
    Endpoints:
    - GET /api/salary/logs/ - List salary payments
    - POST /api/salary/pay/ - Record a new salary payment
    - GET /api/salary/logs/{id}/ - Get salary payment details
    - PATCH /api/salary/logs/{id}/ - Update salary payment
    """
    queryset = SalaryPayment.objects.all().select_related('staff', 'paid_by')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'status', 'payment_date']
    search_fields = ['staff__email', 'staff__first_name', 'staff__last_name', 'notes']
    ordering_fields = ['payment_date', 'amount_due', 'amount_paid', 'status']
    ordering = ['-payment_date']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']  # No PUT or DELETE
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsOwnerOrStaff]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        Staff can only see their own salary payments.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Role-based filtering
        if user.is_staff and user.is_superuser:
            # Admins see everything
            pass
        elif user.is_staff:
            # Regular staff see only their own
            queryset = queryset.filter(staff=user)
        else:
            return queryset.none()
        
        # Staff ID filtering (for admins)
        staff_id = self.request.query_params.get('staff_id')
        if staff_id and (user.is_staff and user.is_superuser):
            queryset = queryset.filter(staff_id=staff_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return SalaryPaymentListSerializer
        elif self.action == 'retrieve':
            return SalaryPaymentDetailSerializer
        elif self.action == 'create':
            return SalaryPaymentCreateSerializer
        else:
            return SalaryPaymentUpdateSerializer
    
    @extend_schema(
        summary="List salary payments",
        description="Get a paginated list of salary payments. Staff see only their own.",
        parameters=[
            OpenApiParameter(name='staff_id', type=str, description='Filter by staff UUID (admin only)'),
            OpenApiParameter(name='status', type=str, description='Filter by status'),
        ],
        responses={200: SalaryPaymentListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List salary payments."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Record a salary payment",
        description="Record a new salary payment for a staff member. Admin only.",
        request=SalaryPaymentCreateSerializer,
        responses={
            201: SalaryPaymentDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        """Record a new salary payment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        salary_payment = serializer.save()
        
        # Notify staff member
        create_notification(
            recipient=salary_payment.staff,
            message=f"Salary payment of ₦{salary_payment.amount_paid:,.2f} has been recorded for {salary_payment.payment_date.strftime('%B %Y')}",
            notification_type='salary'
        )
        
        return Response(
            SalaryPaymentDetailSerializer(salary_payment).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get salary payment details",
        description="Retrieve detailed information about a specific salary payment.",
        responses={200: SalaryPaymentDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get salary payment details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update a salary payment",
        description="Update salary payment details. Admin only.",
        request=SalaryPaymentUpdateSerializer,
        responses={200: SalaryPaymentDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        """Update a salary payment."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get staff salary summary",
        description="Get salary summary for a specific staff member. Admin only.",
        responses={200: OpenApiResponse(description="Salary summary")}
    )
    @action(detail=False, methods=['get'], url_path='staff-summary/(?P<staff_id>[^/.]+)')
    def staff_summary(self, request, staff_id=None):
        """
        Get salary summary for a staff member.
        
        URL: /api/salary/logs/staff-summary/{staff_id}/
        """
        try:
            staff = User.objects.get(id=staff_id, is_staff=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Staff member not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summary = calculate_staff_salary_summary(staff)
        
        return Response({
            'staff': {
                'id': str(staff.id),
                'email': staff.email,
                'full_name': staff.get_full_name()
            },
            'total_due': str(summary['total_due']),
            'total_paid': str(summary['total_paid']),
            'total_remaining': str(summary['total_remaining']),
            'payment_count': summary['payment_count'],
            'pending_count': summary['pending_count'],
            'complete_count': summary['complete_count']
        })


# ============================================================================
# OFFICE EXPENSE VIEWSET
# ============================================================================

@extend_schema(tags=['Office Expenses'])
class OfficeExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing office expenses.
    
    Permissions:
    - List/Retrieve: Staff (all expenses) or Owner (own expenses)
    - Create: Staff only
    - Update: Owner (pending only) or Admin
    - Approve/Reject/Mark Paid: Admin only
    - Delete: Admin (pending/rejected only)
    
    Endpoints:
    - GET /api/expenses/ - List expenses
    - POST /api/expenses/ - Submit new expense
    - GET /api/expenses/{id}/ - Get expense details
    - PATCH /api/expenses/{id}/ - Update expense (pending only)
    - DELETE /api/expenses/{id}/ - Delete expense
    - PATCH /api/expenses/{id}/approve/ - Approve expense
    - PATCH /api/expenses/{id}/reject/ - Reject expense
    - PATCH /api/expenses/{id}/mark-paid/ - Mark expense as paid
    - GET /api/expenses/summary/ - Get expense summary/analytics
    - GET /api/expenses/pending/ - Get pending expenses for approval
    """
    queryset = OfficeExpense.objects.all().select_related(
        'submitted_by', 'approved_by', 'paid_by'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'submitted_by', 'approved_by']
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['expense_date', 'amount', 'created_at', 'status']
    ordering = ['-expense_date', '-created_at']
    permission_classes = [CanManageExpenses]
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        # Non-admin staff only see own expenses
        if user.is_staff and not user.is_superuser:
            queryset = queryset.filter(submitted_by=user)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return OfficeExpenseListSerializer
        elif self.action == 'retrieve':
            return OfficeExpenseDetailSerializer
        elif self.action == 'create':
            return OfficeExpenseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OfficeExpenseUpdateSerializer
        elif self.action == 'approve':
            return OfficeExpenseApproveSerializer
        elif self.action == 'reject':
            return OfficeExpenseRejectSerializer
        elif self.action == 'mark_paid':
            return OfficeExpenseMarkPaidSerializer
        return OfficeExpenseDetailSerializer
    
    @extend_schema(
        summary="List expenses",
        description="Get a paginated list of office expenses with optional filtering.",
        parameters=[
            OpenApiParameter(name='status', type=str, description='Filter by status'),
            OpenApiParameter(name='category', type=str, description='Filter by category'),
            OpenApiParameter(name='start_date', type=str, description='Filter from date'),
            OpenApiParameter(name='end_date', type=str, description='Filter to date'),
        ],
        responses={200: OfficeExpenseListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List expenses."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Submit a new expense",
        description="Submit a new office expense. Staff only.",
        request=OfficeExpenseCreateSerializer,
        responses={
            201: OfficeExpenseDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        """Submit a new expense."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        
        # Notify all admins
        notify_all_admins(
            f"New expense submitted: {expense.title} (₦{expense.amount:,.2f}) by {expense.submitted_by.get_full_name()}",
            'expense'
        )
        
        return Response(
            OfficeExpenseDetailSerializer(expense).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get expense details",
        description="Retrieve detailed information about a specific expense.",
        responses={200: OfficeExpenseDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get expense details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update an expense",
        description="Update expense details. Only pending expenses can be updated.",
        request=OfficeExpenseUpdateSerializer,
        responses={200: OfficeExpenseDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        """Update an expense (pending only)."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete an expense",
        description="Delete an expense. Admin only, pending/rejected expenses only.",
        responses={204: OpenApiResponse(description="Expense deleted")}
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an expense."""
        expense = self.get_object()
        
        if expense.status not in ['pending', 'rejected']:
            return Response(
                {'detail': 'Only pending or rejected expenses can be deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Approve an expense",
        description="Approve a pending expense. Admin only.",
        request=OfficeExpenseApproveSerializer,
        responses={200: OfficeExpenseDetailSerializer}
    )
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve an expense."""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response(
                {'detail': 'Only pending expenses can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        expense.approve(request.user)
        
        # Update notes if provided
        if serializer.validated_data.get('notes'):
            expense.notes = serializer.validated_data['notes']
            expense.save()
        
        # Notify submitter
        create_notification(
            recipient=expense.submitted_by,
            message=f"Your expense '{expense.title}' has been approved.",
            notification_type='expense'
        )
        
        return Response(OfficeExpenseDetailSerializer(expense).data)
    
    @extend_schema(
        summary="Reject an expense",
        description="Reject a pending expense with reason. Admin only.",
        request=OfficeExpenseRejectSerializer,
        responses={200: OfficeExpenseDetailSerializer}
    )
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject an expense."""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response(
                {'detail': 'Only pending expenses can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rejection_reason = serializer.validated_data['rejection_reason']
        expense.reject(request.user, rejection_reason)
        
        # Notify submitter
        create_notification(
            recipient=expense.submitted_by,
            message=f"Your expense '{expense.title}' has been rejected. Reason: {rejection_reason}",
            notification_type='expense'
        )
        
        return Response(OfficeExpenseDetailSerializer(expense).data)
    
    @extend_schema(
        summary="Mark expense as paid",
        description="Mark an approved expense as paid. Admin only.",
        request=OfficeExpenseMarkPaidSerializer,
        responses={200: OfficeExpenseDetailSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """Mark an expense as paid."""
        expense = self.get_object()
        
        if expense.status != 'approved':
            return Response(
                {'detail': 'Only approved expenses can be marked as paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_method = serializer.validated_data['payment_method']
        expense.mark_as_paid(request.user, payment_method)
        
        # Update notes if provided
        if serializer.validated_data.get('notes'):
            expense.notes = serializer.validated_data['notes']
            expense.save()
        
        # Notify submitter
        create_notification(
            recipient=expense.submitted_by,
            message=f"Your expense '{expense.title}' has been paid (₦{expense.amount:,.2f}).",
            notification_type='expense'
        )
        
        return Response(OfficeExpenseDetailSerializer(expense).data)
    
    @extend_schema(
        summary="Get expense summary",
        description="Get expense analytics and summary with optional filters. Admin only.",
        parameters=[
            OpenApiParameter(name='start_date', type=str, description='Filter from date'),
            OpenApiParameter(name='end_date', type=str, description='Filter to date'),
            OpenApiParameter(name='status', type=str, description='Filter by status'),
            OpenApiParameter(name='category', type=str, description='Filter by category'),
        ],
        responses={200: OpenApiResponse(description="Expense summary")}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def summary(self, request):
        """Get expense summary and analytics."""
        from datetime import datetime
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        category_filter = request.query_params.get('category')
        
        # Convert date strings to date objects
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        summary = calculate_expense_summary(
            start_date=start_date,
            end_date=end_date,
            status=status_filter,
            category=category_filter
        )
        
        # Convert Decimal to string for JSON serialization
        for key, value in summary.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                if isinstance(value, dict):
                    summary[key] = {k: str(v) if hasattr(v, 'quantize') else v for k, v in value.items()}
            elif hasattr(value, 'quantize'):  # Decimal
                summary[key] = str(value)
        
        return Response(summary)
    
    @extend_schema(
        summary="Get pending expenses",
        description="Get all pending expenses that need approval. Admin only.",
        responses={200: OfficeExpenseListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """Get all pending expenses for approval."""
        from .utils import get_pending_expenses_for_approval
        
        pending_expenses = get_pending_expenses_for_approval()
        serializer = OfficeExpenseListSerializer(pending_expenses, many=True)
        
        return Response(serializer.data)


# ============================================================================
# NOTIFICATION VIEWSET
# ============================================================================

@extend_schema(tags=['Notifications'])
class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    
    Permissions:
    - List/Retrieve: User sees only their own notifications
    - Create: Admin only (system usually creates these)
    - Update: Not allowed
    - Delete: User can delete their own notifications
    
    Endpoints:
    - GET /api/notifications/ - List user's notifications
    - GET /api/notifications/{id}/ - Get notification details
    - GET /api/notifications/unread/ - Get unread notifications
    - GET /api/notifications/unread/count/ - Get unread count
    - PATCH /api/notifications/{id}/mark-read/ - Mark as read
    - PATCH /api/notifications/mark-all-read/ - Mark all as read
    - DELETE /api/notifications/{id}/ - Delete notification
    - DELETE /api/notifications/clear-all/ - Clear all read notifications
    """
    queryset = Notification.objects.all().select_related('recipient')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset to only show user's own notifications."""
        return super().get_queryset().filter(recipient=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @extend_schema(
        summary="List notifications",
        description="Get a paginated list of user's notifications.",
        parameters=[
            OpenApiParameter(name='type', type=str, description='Filter by notification type'),
            OpenApiParameter(name='is_read', type=bool, description='Filter by read status'),
        ],
        responses={200: NotificationSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List user's notifications."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create notification",
        description="Create a new notification. Admin only. Usually created by system.",
        request=NotificationCreateSerializer,
        responses={201: NotificationSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a notification (admin only)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get notification details",
        description="Retrieve detailed information about a specific notification.",
        responses={200: NotificationSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get notification details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete notification",
        description="Delete a notification.",
        responses={204: OpenApiResponse(description="Notification deleted")}
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a notification."""
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get unread notifications",
        description="Get all unread notifications for the authenticated user.",
        parameters=[
            OpenApiParameter(name='type', type=str, description='Filter by notification type'),
            OpenApiParameter(name='limit', type=int, description='Limit number of results'),
        ],
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        queryset = self.get_queryset().filter(is_read=False)
        
        # Apply type filter if provided
        notification_type = request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        # Apply limit if provided
        limit = request.query_params.get('limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @extend_schema(
        summary="Get unread count",
        description="Get the count of unread notifications. Lightweight endpoint for badges.",
        responses={
            200: OpenApiResponse(
                description="Unread notification count",
                response={'type': 'object', 'properties': {'unread_count': {'type': 'integer'}}}
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='unread/count')
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @extend_schema(
        summary="Mark notification as read",
        description="Mark a specific notification as read.",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response(NotificationSerializer(notification).data)
    
    @extend_schema(
        summary="Mark all as read",
        description="Mark all user's notifications as read.",
        responses={
            200: OpenApiResponse(
                description="All notifications marked as read",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'count': {'type': 'integer'}
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['patch'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        unread_notifications = self.get_queryset().filter(is_read=False)
        count = unread_notifications.count()
        
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': 'All notifications marked as read.',
            'count': count
        })
    
    @extend_schema(
        summary="Clear all read notifications",
        description="Delete all read notifications for the authenticated user.",
        responses={
            200: OpenApiResponse(
                description="Read notifications cleared",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'count': {'type': 'integer'}
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        """Delete all read notifications."""
        read_notifications = self.get_queryset().filter(is_read=True)
        count = read_notifications.count()
        read_notifications.delete()
        
        return Response({
            'message': 'All read notifications cleared.',
            'count': count
        })
