"""
URL Configuration for NewCodeCrafters API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    CohortViewSet,
    PaymentPlanViewSet,
    PaymentLogViewSet,
    SalaryPaymentViewSet,
    OfficeExpenseViewSet,
    NotificationViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Register all viewsets
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'cohorts', CohortViewSet, basename='cohort')
router.register(r'payments/plans', PaymentPlanViewSet, basename='payment-plan')
router.register(r'payments/logs', PaymentLogViewSet, basename='payment-log')
router.register(r'salary/logs', SalaryPaymentViewSet, basename='salary')
router.register(r'expenses', OfficeExpenseViewSet, basename='expense')
router.register(r'notifications', NotificationViewSet, basename='notification')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
Available Endpoints:

COURSES:
- GET    /api/courses/                    - List all courses
- POST   /api/courses/                    - Create new course
- GET    /api/courses/{id}/               - Get course details
- PATCH  /api/courses/{id}/               - Update course
- DELETE /api/courses/{id}/               - Delete course

COHORTS:
- GET    /api/cohorts/                    - List all cohorts
- POST   /api/cohorts/                    - Create new cohort
- GET    /api/cohorts/{id}/               - Get cohort details
- PATCH  /api/cohorts/{id}/               - Update cohort
- DELETE /api/cohorts/{id}/               - Delete cohort
- PATCH  /api/cohorts/{id}/assign-students/     - Assign students to cohort
- PATCH  /api/cohorts/{id}/remove-students/     - Remove students from cohort

PAYMENT PLANS:
- GET    /api/payments/plans/             - List payment plans
- POST   /api/payments/plans/             - Create payment plan
- GET    /api/payments/plans/{id}/        - Get payment plan details
- PATCH  /api/payments/plans/{id}/        - Update payment plan
- DELETE /api/payments/plans/{id}/        - Delete payment plan

PAYMENT LOGS:
- GET    /api/payments/logs/              - List payment logs
- POST   /api/payments/logs/              - Record new payment
- GET    /api/payments/logs/{id}/         - Get payment log details
- GET    /api/payments/logs/student-summary/{student_id}/  - Get student payment summary

SALARY PAYMENTS:
- GET    /api/salary/logs/                - List salary payments
- POST   /api/salary/pay/                 - Record salary payment
- GET    /api/salary/logs/{id}/           - Get salary payment details
- PATCH  /api/salary/logs/{id}/           - Update salary payment
- GET    /api/salary/logs/staff-summary/{staff_id}/  - Get staff salary summary

OFFICE EXPENSES:
- GET    /api/expenses/                   - List expenses
- POST   /api/expenses/                   - Submit new expense
- GET    /api/expenses/{id}/              - Get expense details
- PATCH  /api/expenses/{id}/              - Update expense
- DELETE /api/expenses/{id}/              - Delete expense
- PATCH  /api/expenses/{id}/approve/      - Approve expense
- PATCH  /api/expenses/{id}/reject/       - Reject expense
- PATCH  /api/expenses/{id}/mark-paid/    - Mark expense as paid
- GET    /api/expenses/summary/           - Get expense analytics
- GET    /api/expenses/pending/           - Get pending expenses

NOTIFICATIONS:
- GET    /api/notifications/              - List notifications
- GET    /api/notifications/{id}/         - Get notification details
- DELETE /api/notifications/{id}/         - Delete notification
- GET    /api/notifications/unread/       - Get unread notifications
- GET    /api/notifications/unread/count/ - Get unread count
- PATCH  /api/notifications/{id}/mark-read/      - Mark as read
- PATCH  /api/notifications/mark-all-read/       - Mark all as read
- DELETE /api/notifications/clear-all/           - Clear all read
"""