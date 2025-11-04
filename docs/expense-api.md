# Office Expense API Specification

## Overview
Office expense management allows admins and authorized staff to track, approve, and manage company expenses.

---

## 🔹 OFFICE EXPENSE MODULE

### Models
- **OfficeExpense**(id, title, description, category, amount, expense_date, status, payment_method, receipt_url, submitted_by, approved_by, paid_by, notes, rejection_reason, approved_at, paid_at, created_at, updated_at)

### Categories
- utilities
- rent
- internet
- equipment
- supplies (Office Supplies)
- maintenance
- transportation
- marketing
- software (Software/Subscriptions)
- miscellaneous

### Status Flow
1. **pending** → Initial state when expense is submitted
2. **approved** → Admin approves the expense
3. **paid** → Payment has been processed
4. **rejected** → Admin rejects the expense

---

## API ENDPOINTS

### POST /expenses/
Create a new office expense.

**Permission:** Authenticated (Admin or Staff)

**Request:**
```json
{
  "title": "Internet Bill - January",
  "description": "Monthly internet subscription for office",
  "category": "internet",
  "amount": 50000,
  "expense_date": "2025-01-15",
  "receipt_url": "https://example.com/receipt.pdf",
  "notes": "Payment due by end of month"
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "Expense submitted successfully.",
  "status": "pending"
}
```

**Trigger:**
- Notify all admins about new expense submission

---

### GET /expenses/
List all office expenses with filters.

**Permission:** Admin (all expenses), Staff (only their submitted expenses)

**Query Parameters:**
- `status` - Filter by status (pending, approved, paid, rejected)
- `category` - Filter by category
- `start_date` - Filter expenses from this date
- `end_date` - Filter expenses until this date
- `submitted_by` - Filter by submitter user ID

**Response:**
```json
{
  "count": 25,
  "next": "http://api.example.com/expenses/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Internet Bill - January",
      "description": "Monthly internet subscription",
      "category": "internet",
      "amount": "50000.00",
      "expense_date": "2025-01-15",
      "status": "pending",
      "payment_method": null,
      "receipt_url": "https://example.com/receipt.pdf",
      "submitted_by": {
        "id": "uuid",
        "email": "staff@example.com",
        "full_name": "John Doe"
      },
      "approved_by": null,
      "paid_by": null,
      "notes": "Payment due by end of month",
      "created_at": "2025-01-10T10:00:00Z",
      "updated_at": "2025-01-10T10:00:00Z"
    }
  ]
}
```

---

### GET /expenses/{id}/
Get details of a specific expense.

**Permission:** Admin (any expense), Staff (only their own)

**Response:**
```json
{
  "id": "uuid",
  "title": "Internet Bill - January",
  "description": "Monthly internet subscription for office",
  "category": "internet",
  "amount": "50000.00",
  "expense_date": "2025-01-15",
  "status": "approved",
  "payment_method": null,
  "receipt_url": "https://example.com/receipt.pdf",
  "submitted_by": {
    "id": "uuid",
    "email": "staff@example.com",
    "full_name": "John Doe"
  },
  "approved_by": {
    "id": "uuid",
    "email": "admin@example.com",
    "full_name": "Jane Admin"
  },
  "paid_by": null,
  "notes": "Payment due by end of month",
  "rejection_reason": "",
  "approved_at": "2025-01-11T09:00:00Z",
  "paid_at": null,
  "created_at": "2025-01-10T10:00:00Z",
  "updated_at": "2025-01-11T09:00:00Z"
}
```

---

### PATCH /expenses/{id}/
Update an expense (limited fields based on status).

**Permission:** 
- Staff can update their pending expenses
- Admin can update any expense

**Request (Staff - pending expense):**
```json
{
  "title": "Internet Bill - January (Updated)",
  "amount": 55000,
  "notes": "Price increased"
}
```

**Request (Admin - any expense):**
```json
{
  "status": "approved",
  "notes": "Approved for payment"
}
```

**Response:**
```json
{
  "message": "Expense updated successfully."
}
```

---

### PATCH /expenses/{id}/approve/
Approve a pending expense.

**Permission:** Admin only

**Request:**
```json
{
  "notes": "Approved - necessary expense"
}
```

**Response:**
```json
{
  "message": "Expense approved successfully.",
  "approved_at": "2025-01-11T09:00:00Z"
}
```

**Trigger:**
- Send notification to submitter
- Update expense status to "approved"

---

### PATCH /expenses/{id}/reject/
Reject a pending expense.

**Permission:** Admin only

**Request:**
```json
{
  "rejection_reason": "Duplicate submission - already paid last month"
}
```

**Response:**
```json
{
  "message": "Expense rejected.",
  "rejection_reason": "Duplicate submission - already paid last month"
}
```

**Trigger:**
- Send notification to submitter with rejection reason

---

### PATCH /expenses/{id}/mark-paid/
Mark an approved expense as paid.

**Permission:** Admin only

**Request:**
```json
{
  "payment_method": "transfer",
  "notes": "Paid via bank transfer on 2025-01-15"
}
```

**Response:**
```json
{
  "message": "Expense marked as paid.",
  "paid_at": "2025-01-15T14:30:00Z"
}
```

**Trigger:**
- Send notification to submitter
- Update expense status to "paid"

---

### DELETE /expenses/{id}/
Delete an expense.

**Permission:** 
- Staff can delete their own pending expenses
- Admin can delete any pending or rejected expense

**Response:**
```json
{
  "message": "Expense deleted successfully."
}
```

---

### GET /expenses/summary/
Get expense summary and statistics.

**Permission:** Admin only

**Query Parameters:**
- `start_date` - Start of date range
- `end_date` - End of date range
- `category` - Filter by category

**Response:**
```json
{
  "total_expenses": "500000.00",
  "pending_count": 5,
  "pending_amount": "150000.00",
  "approved_count": 3,
  "approved_amount": "100000.00",
  "paid_count": 10,
  "paid_amount": "250000.00",
  "rejected_count": 2,
  "by_category": {
    "internet": "50000.00",
    "utilities": "100000.00",
    "rent": "200000.00",
    "equipment": "150000.00"
  },
  "monthly_trend": [
    {
      "month": "2025-01",
      "total": "250000.00",
      "count": 8
    },
    {
      "month": "2024-12",
      "total": "200000.00",
      "count": 7
    }
  ]
}
```

---

### GET /expenses/export/
Export expenses to CSV/Excel.

**Permission:** Admin only

**Query Parameters:**
- `format` - csv or xlsx
- `start_date` - Start of date range
- `end_date` - End of date range
- `status` - Filter by status
- `category` - Filter by category

**Response:**
- File download with expenses data

---

## Permission Summary

| Endpoint | Admin | Staff | Student |
|----------|-------|-------|---------|
| POST /expenses/ | ✅ | ✅ | ❌ |
| GET /expenses/ | ✅ (all) | ✅ (own) | ❌ |
| GET /expenses/{id}/ | ✅ | ✅ (own) | ❌ |
| PATCH /expenses/{id}/ | ✅ | ✅ (own, pending) | ❌ |
| DELETE /expenses/{id}/ | ✅ | ✅ (own, pending) | ❌ |
| PATCH /expenses/{id}/approve/ | ✅ | ❌ | ❌ |
| PATCH /expenses/{id}/reject/ | ✅ | ❌ | ❌ |
| PATCH /expenses/{id}/mark-paid/ | ✅ | ❌ | ❌ |
| GET /expenses/summary/ | ✅ | ❌ | ❌ |
| GET /expenses/export/ | ✅ | ❌ | ❌ |

---

## Notification Triggers

1. **New Expense Submitted** → Notify all admins
2. **Expense Approved** → Notify submitter
3. **Expense Rejected** → Notify submitter with reason
4. **Expense Paid** → Notify submitter

---

## Validation Rules

1. **Amount** must be greater than 0
2. **Expense date** cannot be in the future
3. **Category** must be one of the predefined choices
4. **Status transitions:**
   - pending → approved OR rejected
   - approved → paid
   - rejected → (terminal state)
   - paid → (terminal state)
5. **Receipt URL** must be valid URL format (optional)
6. Staff can only submit expenses, not approve/reject/pay
7. Only pending expenses can be edited by staff
8. Only approved expenses can be marked as paid

---

## Frontend Dashboard Components

### Admin Dashboard
- `/admin/expenses` - List all expenses with filters
- `/admin/expenses/pending` - Quick view of pending approvals
- `/admin/expenses/summary` - Financial summary and charts
- `/admin/expenses/new` - Create new expense
- `/admin/expenses/{id}` - Expense detail with approve/reject/pay actions

### Staff Dashboard
- `/staff/expenses` - List own submitted expenses
- `/staff/expenses/new` - Submit new expense
- `/staff/expenses/{id}` - View expense details

### Charts & Analytics
- Monthly expense trends
- Category-wise breakdown (pie chart)
- Status distribution
- Pending vs paid comparison