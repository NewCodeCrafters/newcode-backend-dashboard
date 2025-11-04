# NewCodeCrafters Models Integration Guide

## Overview
This document explains how the new models integrate with your existing User authentication system.

## Your Existing User Model Fields
Based on your uploaded files, your User model has:
- `user_type` - CharField with choices (from UserTypeChoices)
- `email` - EmailField (unique)
- `first_name` - CharField
- `last_name` - CharField
- `is_student` - BooleanField
- `is_staff` - BooleanField
- `is_active` - BooleanField
- `otp_verified` - BooleanField
- `status` - Field with StatusChoices

## New Models Created

### 1. **Course** (courses table)
Represents training courses offered by NewCodeCrafters.

**Fields:**
- `id` - UUID primary key
- `title` - Course name
- `description` - Course details
- `duration_weeks` - Course length in weeks
- `created_by` - ForeignKey to User (staff only)
- `created_at`, `updated_at` - Timestamps

**Integration:** Uses `is_staff=True` for admin/instructors who can create courses.

---

### 2. **Cohort** (cohorts table)
Groups of students taking a course together.

**Fields:**
- `id` - UUID primary key
- `name` - Cohort identifier (e.g., "Cohort A")
- `course` - ForeignKey to Course
- `instructor` - ForeignKey to User (staff)
- `students` - ManyToManyField to User (students)
- `start_date`, `end_date` - Date range
- `created_at`, `updated_at` - Timestamps

**Integration:** 
- Uses `is_staff=True` for instructors
- Uses `is_student=True` for students in the cohort

---

### 3. **PaymentPlan** (payment_plans table)
Defines payment structure for each student.

**Fields:**
- `id` - UUID primary key
- `student` - ForeignKey to User (students only)
- `course` - ForeignKey to Course
- `cohort` - ForeignKey to Cohort (optional)
- `plan_type` - Choice: 'full', '50/50', 'installment'
- `amount_total` - Total course fee
- `amount_paid` - Amount paid so far
- `status` - 'pending', 'partial', 'complete', 'overdue'
- `created_at`, `updated_at` - Timestamps

**Computed Properties:**
- `amount_remaining` - Calculates remaining balance
- `payment_percentage` - Calculates % paid

**Methods:**
- `update_status()` - Auto-updates status based on payments

**Integration:** Uses `is_student=True` to link to student users.

---

### 4. **PaymentLog** (payment_logs table)
Records individual payment transactions.

**Fields:**
- `id` - UUID primary key
- `payment_plan` - ForeignKey to PaymentPlan
- `student` - ForeignKey to User (students)
- `amount` - Payment amount
- `payment_method` - 'transfer', 'cash', 'card', 'mobile'
- `receipt_url` - Link to receipt/proof
- `payment_date` - When payment was made
- `recorded_by` - ForeignKey to User (staff/admin)
- `notes` - Additional info
- `created_at` - Timestamp

**Integration:**
- `student` uses `is_student=True`
- `recorded_by` uses `is_staff=True` (admin recording payment)

---

### 5. **SalaryPayment** (salary_payments table)
Tracks salary payments to staff members.

**Fields:**
- `id` - UUID primary key
- `staff` - ForeignKey to User (staff)
- `amount_due` - Expected salary amount
- `amount_paid` - Actual amount paid
- `status` - 'pending', 'partial', 'complete'
- `paid_by` - ForeignKey to User (admin)
- `payment_date` - When salary was paid
- `notes` - Additional info
- `created_at`, `updated_at` - Timestamps

**Computed Properties:**
- `amount_remaining` - Calculates unpaid balance

**Integration:**
- `staff` uses `is_staff=True`
- `paid_by` uses `is_staff=True AND is_superuser=True`

---

### 6. **OfficeExpense** (office_expenses table)
Tracks company operational expenses.

**Fields:**
- `id` - UUID primary key
- `title` - Brief description
- `description` - Detailed info
- `category` - 10 categories (utilities, rent, internet, equipment, etc.)
- `amount` - Expense amount
- `expense_date` - When expense occurred
- `status` - 'pending', 'approved', 'paid', 'rejected'
- `payment_method` - 'transfer', 'cash', 'card', 'mobile', 'cheque'
- `receipt_url` - Link to receipt/invoice
- `submitted_by` - ForeignKey to User (who submitted)
- `approved_by` - ForeignKey to User (admin who approved)
- `paid_by` - ForeignKey to User (admin who paid)
- `notes` - General notes
- `rejection_reason` - If rejected, why
- `approved_at`, `paid_at` - Timestamps
- `created_at`, `updated_at` - Timestamps

**Methods:**
- `approve(admin_user)` - Approve expense
- `reject(admin_user, reason)` - Reject expense
- `mark_as_paid(admin_user, payment_method)` - Mark as paid

**Integration:** All user fields use `is_staff=True` for staff/admin access.

---

### 7. **Notification** (notifications table)
Real-time alerts and messages for users.

**Fields:**
- `id` - UUID primary key
- `recipient` - ForeignKey to User
- `message` - Notification text
- `type` - 'verification', 'role_assignment', 'payment', 'salary', 'cohort', 'expense', 'general'
- `is_read` - Boolean flag
- `created_at` - When notification was created
- `read_at` - When user read it

**Methods:**
- `mark_as_read()` - Mark notification as read

**Integration:** Works with any user type via `recipient` field.

---

## User Role Mapping

Your existing User model uses:
- `is_staff` - For instructors/admins who manage the system
- `is_student` - For students enrolled in courses
- `is_superuser` - For top-level admins (payment approvals, etc.)

### Role Permissions Matrix

| Action | is_superuser | is_staff | is_student |
|--------|--------------|----------|------------|
| Create Course | ✅ | ✅ | ❌ |
| Create Cohort | ✅ | ✅ | ❌ |
| Assign Students to Cohort | ✅ | ✅ | ❌ |
| Create Payment Plan | ✅ | ❌ | ❌ |
| Record Payment | ✅ | ✅ | ❌ |
| View Own Payments | ✅ | ❌ | ✅ |
| Pay Salary | ✅ | ❌ | ❌ |
| View Own Salary | ✅ | ✅ | ❌ |
| Submit Expense | ✅ | ✅ | ❌ |
| Approve/Reject Expense | ✅ | ✅ | ❌ |
| Pay Expense | ✅ | ✅ | ❌ |
| View All Notifications | ✅ | - | - |
| View Own Notifications | ✅ | ✅ | ✅ |

---

## Database Setup Steps

### 1. Add to your Django app's models.py
```python
# Copy the entire content of the models.py file
# It already imports: from django.contrib.auth import get_user_model
# And uses: User = get_user_model()
```

### 2. Add to your Django app's admin.py
```python
# Copy the entire content of the admin.py file
# It provides Django admin interfaces for all models
```

### 3. Create migrations
```bash
python manage.py makemigrations
```

### 4. Review the migration file
Check the generated migration to ensure it looks correct.

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Update existing users (if needed)
If you have existing users who should be students/staff, update them:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Mark users as students
User.objects.filter(email__in=['student1@example.com']).update(is_student=True)

# Mark users as staff
User.objects.filter(email__in=['instructor@example.com']).update(is_staff=True)
```

---

## API Endpoints to Implement

Based on the project scope document, you'll need to create these API endpoints:

### Courses
- `GET /api/courses/` - List all courses
- `POST /api/courses/` - Create course (Admin)
- `GET /api/courses/{id}/` - Get course details
- `PATCH /api/courses/{id}/` - Update course (Admin)
- `DELETE /api/courses/{id}/` - Delete course (Admin)

### Cohorts
- `GET /api/cohorts/` - List cohorts
- `POST /api/cohorts/` - Create cohort (Admin)
- `GET /api/cohorts/{id}/` - Get cohort details
- `PATCH /api/cohorts/{id}/assign-students/` - Assign students
- `DELETE /api/cohorts/{id}/` - Delete cohort (Admin)

### Payment Plans
- `GET /api/payments/plans/` - List payment plans
- `POST /api/payments/plans/` - Create plan (Admin)
- `GET /api/payments/plans/{id}/` - Get plan details
- `PATCH /api/payments/plans/{id}/` - Update plan (Admin)

### Payment Logs
- `GET /api/payments/logs/` - List payments (with filters)
- `POST /api/payments/logs/` - Record payment (Admin/Staff)
- `GET /api/payments/logs/?student_id={uuid}` - Student's payment history

### Salaries
- `GET /api/salary/logs/` - List salary payments
- `POST /api/salary/pay/` - Record salary (Admin)
- `GET /api/salary/logs/?staff_id={uuid}` - Staff's salary history

### Office Expenses
- `GET /api/expenses/` - List expenses (with filters)
- `POST /api/expenses/` - Submit expense (Staff/Admin)
- `GET /api/expenses/{id}/` - Get expense details
- `PATCH /api/expenses/{id}/` - Update expense
- `PATCH /api/expenses/{id}/approve/` - Approve expense (Admin)
- `PATCH /api/expenses/{id}/reject/` - Reject expense (Admin)
- `PATCH /api/expenses/{id}/mark-paid/` - Mark as paid (Admin)
- `GET /api/expenses/summary/` - Expense analytics (Admin)
- `DELETE /api/expenses/{id}/` - Delete expense

### Notifications
- `GET /api/notifications/` - List user's notifications
- `PATCH /api/notifications/{id}/read/` - Mark as read
- `WebSocket /ws/notifications/{user_id}/` - Real-time notifications

---

## Next Steps

1. ✅ Models created and integrated with your User model
2. ✅ Admin interfaces configured
3. ⏳ Create serializers for API endpoints
4. ⏳ Create ViewSets/Views for business logic
5. ⏳ Create URL routing
6. ⏳ Create permission classes
7. ⏳ Create signal handlers for notifications
8. ⏳ Implement WebSocket consumers

---

## Testing Checklist

After migrations:
- [ ] Create test users with different roles (student, staff, admin)
- [ ] Create test courses via Django admin
- [ ] Create test cohorts and assign students
- [ ] Create payment plans for students
- [ ] Record test payments
- [ ] Record test salary payments
- [ ] Submit test expenses
- [ ] Test expense approval workflow
- [ ] Check all Django admin interfaces
- [ ] Verify all model relationships work correctly

---

## Important Notes

1. **Foreign Key Constraints:** All foreign keys use `on_delete=models.CASCADE` or `on_delete=models.SET_NULL` to handle data integrity.

2. **User Queries:** Always use `get_user_model()` instead of importing User directly for better compatibility.

3. **Permissions:** The `limit_choices_to` on foreign keys provides database-level filtering, but you'll need additional permission classes for API endpoints.

4. **UUIDs:** All models use UUID primary keys for better security and distributed systems support.

5. **Timestamps:** All models track creation and update times automatically.

6. **Computed Properties:** PaymentPlan and SalaryPayment have `@property` methods that calculate derived values without storing them in the database.

7. **Helper Methods:** OfficeExpense has `approve()`, `reject()`, and `mark_as_paid()` methods to encapsulate business logic.

---

## Support

For any issues or questions:
1. Check the API specification document (OFFICE_EXPENSE_API.md)
2. Review the original project scope (NCC_Project_SCOPE.pdf)
3. Test in Django admin first before building API endpoints