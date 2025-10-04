-- ============================================
-- ACADEMY MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================

-- 1. USER MANAGEMENT TABLES
-- ============================================

-- Base User Table (for authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT FALSE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('STUDENT', 'STAFF', 'ADMIN')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Email Verification OTP Table
CREATE TABLE email_verification_otp (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    otp VARCHAR(6) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Admin Table
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_level VARCHAR(20) DEFAULT 'STANDARD' CHECK (admin_level IN ('SUPER', 'STANDARD')),
    permissions JSONB, -- Store specific permissions as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff Table
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    joining_date DATE NOT NULL,
    salary DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    date_of_birth DATE,
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    onboarded_by INTEGER REFERENCES admins(id),
    onboarding_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. BATCH MANAGEMENT TABLES
-- ============================================

-- Batch Table
CREATE TABLE batches (
    id SERIAL PRIMARY KEY,
    batch_name VARCHAR(100) NOT NULL,
    batch_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    max_students INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER NOT NULL REFERENCES admins(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_date_range CHECK (end_date > start_date)
);

-- Student Batch Enrollment
CREATE TABLE student_batch_enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    enrolled_by INTEGER NOT NULL REFERENCES admins(id),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'DROPPED', 'SUSPENDED')),
    total_fee DECIMAL(10, 2) NOT NULL, -- Total fee for this student (can be different from batch price)
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    final_fee DECIMAL(10, 2) NOT NULL, -- After discount
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, batch_id)
);

-- ============================================
-- 3. PAYMENT MANAGEMENT TABLES
-- ============================================

-- Payment Plans (for installments)
CREATE TABLE payment_plans (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES student_batch_enrollments(id) ON DELETE CASCADE,
    plan_name VARCHAR(100) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    number_of_installments INTEGER NOT NULL,
    created_by INTEGER NOT NULL REFERENCES admins(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Installments Schedule
CREATE TABLE installments (
    id SERIAL PRIMARY KEY,
    payment_plan_id INTEGER NOT NULL REFERENCES payment_plans(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'OVERDUE', 'WAIVED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(payment_plan_id, installment_number)
);

-- Payment Transactions
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES student_batch_enrollments(id) ON DELETE CASCADE,
    installment_id INTEGER REFERENCES installments(id), -- NULL if full payment
    student_id INTEGER NOT NULL REFERENCES students(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('CASH', 'CARD', 'BANK_TRANSFER', 'UPI', 'CHEQUE', 'ONLINE')),
    transaction_id VARCHAR(100) UNIQUE,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_status VARCHAR(20) DEFAULT 'SUCCESS' CHECK (payment_status IN ('SUCCESS', 'PENDING', 'FAILED', 'REFUNDED')),
    notes TEXT,
    received_by INTEGER NOT NULL REFERENCES admins(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payment Summary View (for quick access)
CREATE TABLE payment_summary (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER UNIQUE NOT NULL REFERENCES student_batch_enrollments(id) ON DELETE CASCADE,
    total_fee DECIMAL(10, 2) NOT NULL,
    total_paid DECIMAL(10, 2) DEFAULT 0,
    total_pending DECIMAL(10, 2) NOT NULL,
    last_payment_date DATE,
    next_due_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. NOTIFICATION TABLES
-- ============================================

-- Admin Notifications
CREATE TABLE admin_notifications (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('NEW_SIGNUP', 'PAYMENT_RECEIVED', 'PAYMENT_OVERDUE', 'BATCH_CREATED', 'STUDENT_ENROLLED', 'SYSTEM')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_user_id INTEGER REFERENCES users(id),
    related_batch_id INTEGER REFERENCES batches(id),
    related_payment_id INTEGER REFERENCES payment_transactions(id),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email Notification Queue
CREATE TABLE email_queue (
    id SERIAL PRIMARY KEY,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(200),
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    email_type VARCHAR(50) NOT NULL CHECK (email_type IN ('VERIFICATION', 'NEW_SIGNUP_ALERT', 'PAYMENT_CONFIRMATION', 'PAYMENT_REMINDER', 'ENROLLMENT_CONFIRMATION', 'GENERAL')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'FAILED')),
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);

`STOP`


-- ============================================
-- 5. INDEXES FOR PERFORMANCE
-- ============================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Student indexes
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_onboarded_by ON students(onboarded_by);

-- Batch indexes
CREATE INDEX idx_batches_start_date ON batches(start_date);
CREATE INDEX idx_batches_end_date ON batches(end_date);
CREATE INDEX idx_batches_created_by ON batches(created_by);
CREATE INDEX idx_batches_is_active ON batches(is_active);

-- Enrollment indexes
CREATE INDEX idx_enrollments_student_id ON student_batch_enrollments(student_id);
CREATE INDEX idx_enrollments_batch_id ON student_batch_enrollments(batch_id);
CREATE INDEX idx_enrollments_status ON student_batch_enrollments(status);

-- Payment indexes
CREATE INDEX idx_payment_transactions_student_id ON payment_transactions(student_id);
CREATE INDEX idx_payment_transactions_enrollment_id ON payment_transactions(enrollment_id);
CREATE INDEX idx_payment_transactions_payment_date ON payment_transactions(payment_date);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(payment_status);

-- Installment indexes
CREATE INDEX idx_installments_plan_id ON installments(payment_plan_id);
CREATE INDEX idx_installments_due_date ON installments(due_date);
CREATE INDEX idx_installments_status ON installments(status);

-- Notification indexes
CREATE INDEX idx_admin_notifications_admin_id ON admin_notifications(admin_id);
CREATE INDEX idx_admin_notifications_is_read ON admin_notifications(is_read);
CREATE INDEX idx_admin_notifications_created_at ON admin_notifications(created_at);

-- Email queue indexes
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_created_at ON email_queue(created_at);

-- ============================================
-- 6. TRIGGERS AND FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batches_updated_at BEFORE UPDATE ON batches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at BEFORE UPDATE ON student_batch_enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_transactions_updated_at BEFORE UPDATE ON payment_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to notify all admins when new user signs up
CREATE OR REPLACE FUNCTION notify_admins_new_signup()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO admin_notifications (admin_id, notification_type, title, message, related_user_id)
    SELECT 
        a.id,
        'NEW_SIGNUP',
        'New User Registration',
        'A new user ' || NEW.first_name || ' ' || NEW.last_name || ' (' || NEW.email || ') has signed up as ' || NEW.user_type,
        NEW.id
    FROM admins a
    INNER JOIN users u ON a.user_id = u.id
    WHERE u.is_active = TRUE;
    
    -- Add to email queue for all admins
    INSERT INTO email_queue (recipient_email, recipient_name, subject, body, email_type)
    SELECT 
        u.email,
        u.first_name || ' ' || u.last_name,
        'New User Registration - ' || NEW.first_name || ' ' || NEW.last_name,
        'Hello ' || u.first_name || ',\n\nA new user has registered on the academy platform.\n\nDetails:\nName: ' || NEW.first_name || ' ' || NEW.last_name || '\nEmail: ' || NEW.email || '\nUser Type: ' || NEW.user_type || '\nRegistration Date: ' || NEW.created_at || '\n\nPlease review and take necessary action.\n\nBest regards,\nAcademy System',
        'NEW_SIGNUP_ALERT'
    FROM admins a
    INNER JOIN users u ON a.user_id = u.id
    WHERE u.is_active = TRUE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to notify admins on new user signup
CREATE TRIGGER trigger_notify_admins_new_signup
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION notify_admins_new_signup();

-- Function to update payment summary after payment transaction
CREATE OR REPLACE FUNCTION update_payment_summary()
RETURNS TRIGGER AS $$
DECLARE
    v_total_paid DECIMAL(10, 2);
    v_total_fee DECIMAL(10, 2);
    v_next_due_date DATE;
BEGIN
    -- Calculate total paid for this enrollment
    SELECT COALESCE(SUM(amount), 0)
    INTO v_total_paid
    FROM payment_transactions
    WHERE enrollment_id = NEW.enrollment_id
    AND payment_status = 'SUCCESS';
    
    -- Get total fee
    SELECT final_fee
    INTO v_total_fee
    FROM student_batch_enrollments
    WHERE id = NEW.enrollment_id;
    
    -- Get next due date
    SELECT MIN(due_date)
    INTO v_next_due_date
    FROM installments i
    INNER JOIN payment_plans pp ON i.payment_plan_id = pp.id
    WHERE pp.enrollment_id = NEW.enrollment_id
    AND i.status = 'PENDING'
    AND i.due_date > CURRENT_DATE;
    
    -- Update or insert payment summary
    INSERT INTO payment_summary (enrollment_id, total_fee, total_paid, total_pending, last_payment_date, next_due_date)
    VALUES (NEW.enrollment_id, v_total_fee, v_total_paid, v_total_fee - v_total_paid, NEW.payment_date, v_next_due_date)
    ON CONFLICT (enrollment_id)
    DO UPDATE SET
        total_paid = v_total_paid,
        total_pending = v_total_fee - v_total_paid,
        last_payment_date = NEW.payment_date,
        next_due_date = v_next_due_date,
        updated_at = CURRENT_TIMESTAMP;
    
    -- Update installment status if linked
    IF NEW.installment_id IS NOT NULL AND NEW.payment_status = 'SUCCESS' THEN
        UPDATE installments
        SET status = 'PAID'
        WHERE id = NEW.installment_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update payment summary
CREATE TRIGGER trigger_update_payment_summary
AFTER INSERT ON payment_transactions
FOR EACH ROW
EXECUTE FUNCTION update_payment_summary();

-- Function to set OTP expiry time
CREATE OR REPLACE FUNCTION set_otp_expiry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.expires_at = NEW.created_at + INTERVAL '10 minutes';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to set OTP expiry
CREATE TRIGGER trigger_set_otp_expiry
BEFORE INSERT ON email_verification_otp
FOR EACH ROW
EXECUTE FUNCTION set_otp_expiry();

-- ============================================
-- 7. USEFUL VIEWS
-- ============================================

-- View: Active Students with Batch Information
CREATE VIEW v_active_students_with_batches AS
SELECT 
    s.id AS student_id,
    s.student_id AS student_code,
    u.first_name,
    u.last_name,
    u.email,
    u.phone,
    b.batch_name,
    b.batch_code,
    sbe.enrollment_date,
    sbe.final_fee,
    ps.total_paid,
    ps.total_pending,
    ps.next_due_date,
    sbe.status AS enrollment_status
FROM students s
INNER JOIN users u ON s.user_id = u.id
INNER JOIN student_batch_enrollments sbe ON s.id = sbe.student_id
INNER JOIN batches b ON sbe.batch_id = b.id
LEFT JOIN payment_summary ps ON sbe.id = ps.enrollment_id
WHERE s.is_active = TRUE
AND sbe.status = 'ACTIVE';

-- View: Overdue Payments
CREATE VIEW v_overdue_payments AS
SELECT 
    s.student_id AS student_code,
    u.first_name || ' ' || u.last_name AS student_name,
    u.email,
    u.phone,
    b.batch_name,
    i.installment_number,
    i.amount AS due_amount,
    i.due_date,
    CURRENT_DATE - i.due_date AS days_overdue
FROM installments i
INNER JOIN payment_plans pp ON i.payment_plan_id = pp.id
INNER JOIN student_batch_enrollments sbe ON pp.enrollment_id = sbe.id
INNER JOIN students s ON sbe.student_id = s.id
INNER JOIN users u ON s.user_id = u.id
INNER JOIN batches b ON sbe.batch_id = b.id
WHERE i.status = 'PENDING'
AND i.due_date < CURRENT_DATE
ORDER BY i.due_date;

-- View: Batch Revenue Summary
CREATE VIEW v_batch_revenue_summary AS
SELECT 
    b.id AS batch_id,
    b.batch_name,
    b.batch_code,
    b.start_date,
    b.end_date,
    COUNT(DISTINCT sbe.student_id) AS total_students,
    SUM(sbe.final_fee) AS total_expected_revenue,
    SUM(ps.total_paid) AS total_collected,
    SUM(ps.total_pending) AS total_pending
FROM batches b
LEFT JOIN student_batch_enrollments sbe ON b.id = sbe.batch_id
LEFT JOIN payment_summary ps ON sbe.id = ps.enrollment_id
GROUP BY b.id, b.batch_name, b.batch_code, b.start_date, b.end_date
ORDER BY b.start_date DESC;

-- ============================================
-- 8. SAMPLE DATA INSERTION QUERIES
-- ============================================

-- Insert Sample Admin User
/*
INSERT INTO users (email, password_hash, first_name, last_name, phone, is_active, is_email_verified, user_type)
VALUES ('admin@academy.com', 'hashed_password_here', 'Admin', 'User', '+1234567890', TRUE, TRUE, 'ADMIN');

INSERT INTO admins (user_id, admin_level)
VALUES (1, 'SUPER');

-- Insert Sample Batch
INSERT INTO batches (batch_name, batch_code, description, start_date, end_date, price, max_students, created_by)
VALUES ('Web Development Batch 2025', 'WD-2025-01', 'Complete web development course', '2025-01-01', '2025-06-30', 50000.00, 30, 1);

-- Insert Sample Student
INSERT INTO users (email, password_hash, first_name, last_name, phone, is_active, is_email_verified, user_type)
VALUES ('student@example.com', 'hashed_password_here', 'John', 'Doe', '+9876543210', TRUE, TRUE, 'STUDENT');

INSERT INTO students (user_id, student_id, date_of_birth, address, emergency_contact_name, emergency_contact_phone, onboarded_by, onboarding_date)
VALUES (2, 'STU-2025-001', '2000-01-15', '123 Main Street, City', 'Jane Doe', '+9876543211', 1, CURRENT_DATE);

-- Enroll Student in Batch
INSERT INTO student_batch_enrollments (student_id, batch_id, enrolled_by, total_fee, discount_amount, final_fee)
VALUES (1, 1, 1, 50000.00, 5000.00, 45000.00);

-- Create Payment Plan (3 installments)
INSERT INTO payment_plans (enrollment_id, plan_name, total_amount, number_of_installments, created_by)
VALUES (1, '3 Installment Plan', 45000.00, 3, 1);

-- Create Installments
INSERT INTO installments (payment_plan_id, installment_number, amount, due_date)
VALUES 
    (1, 1, 15000.00, '2025-01-15'),
    (1, 2, 15000.00, '2025-03-15'),
    (1, 3, 15000.00, '2025-05-15');
*/