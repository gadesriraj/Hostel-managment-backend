-- ==============================================================================
-- HostelSync - Smart Hostel Management Platform
-- Complete PostgreSQL / Supabase Schema Definition & Seed Script
-- ==============================================================================

-- Enable UUID extension if not already available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'warden', 'staff')),
    phone VARCHAR(30),
    avatar_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. ROOMS TABLE
CREATE TABLE IF NOT EXISTS rooms (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    room_number VARCHAR(30) UNIQUE NOT NULL,
    hostel_name VARCHAR(100) NOT NULL DEFAULT 'Horizon Hall',
    block VARCHAR(50) NOT NULL DEFAULT 'Block A',
    floor INTEGER NOT NULL DEFAULT 1,
    capacity INTEGER NOT NULL DEFAULT 2,
    type VARCHAR(50) DEFAULT 'Standard Double',
    status VARCHAR(30) NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'partially_occupied', 'full', 'maintenance')),
    amenities JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    enrollment_no VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_of_study INTEGER NOT NULL DEFAULT 1,
    gender VARCHAR(20),
    emergency_contact VARCHAR(100),
    blood_group VARCHAR(10),
    room_id VARCHAR(36) REFERENCES rooms(id) ON DELETE SET NULL,
    hostel_name VARCHAR(100) DEFAULT 'Horizon Hall',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. STAFF TABLE
CREATE TABLE IF NOT EXISTS staff (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'busy', 'off_duty')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. ROOM ALLOCATIONS TABLE
CREATE TABLE IF NOT EXISTS room_allocations (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    room_id VARCHAR(36) NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    allocated_by VARCHAR(36) NOT NULL REFERENCES users(id),
    allocation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    vacated_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'vacated', 'transferred')),
    notes TEXT
);

-- 6. COMPLAINTS TABLE
CREATE TABLE IF NOT EXISTS complaints (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    complaint_code VARCHAR(50) UNIQUE NOT NULL,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    room_id VARCHAR(36) REFERENCES rooms(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'resolved', 'rejected')),
    assigned_to VARCHAR(36) REFERENCES staff(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. COMPLAINT ASSIGNMENTS LOG
CREATE TABLE IF NOT EXISTS complaint_assignments (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    complaint_id VARCHAR(36) NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    staff_id VARCHAR(36) NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    assigned_by VARCHAR(36) NOT NULL REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'assigned',
    notes TEXT
);

-- 8. VISITORS TABLE
CREATE TABLE IF NOT EXISTS visitors (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    visitor_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    visit_date VARCHAR(20) NOT NULL,
    entry_time VARCHAR(10) NOT NULL,
    expected_exit_time VARCHAR(10) NOT NULL,
    actual_exit_time VARCHAR(10),
    purpose VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'completed')),
    approved_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. NOTICES TABLE
CREATE TABLE IF NOT EXISTS notices (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'General',
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('normal', 'important', 'urgent')),
    target_audience VARCHAR(20) DEFAULT 'all' CHECK (target_audience IN ('all', 'students', 'staff')),
    published_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. MESS FEEDBACK TABLE
CREATE TABLE IF NOT EXISTS mess_feedback (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'snacks', 'dinner')),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    hygiene_rating INTEGER DEFAULT 4 CHECK (hygiene_rating >= 1 AND hygiene_rating <= 5),
    taste_rating INTEGER DEFAULT 4 CHECK (taste_rating >= 1 AND taste_rating <= 5),
    comments TEXT,
    date VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'system',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_students_room ON students(room_id);
CREATE INDEX IF NOT EXISTS idx_students_enrollment ON students(enrollment_no);
CREATE INDEX IF NOT EXISTS idx_rooms_number ON rooms(room_number);
CREATE INDEX IF NOT EXISTS idx_complaints_student ON complaints(student_id);
CREATE INDEX IF NOT EXISTS idx_complaints_staff ON complaints(assigned_to);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_visitors_student ON visitors(student_id);
CREATE INDEX IF NOT EXISTS idx_notices_priority ON notices(priority);

-- SEED DATA
INSERT INTO users (id, email, password_hash, full_name, role, phone)
VALUES 
    ('usr-warden-1', 'warden@hostelsync.edu', 'admin123', 'Dr. Robert Vance', 'warden', '+1 (555) 234-5678'),
    ('usr-student-1', 'student@hostelsync.edu', 'student123', 'Alex Morgan', 'student', '+1 (555) 345-6789'),
    ('usr-student-2', 'priya@hostelsync.edu', 'student123', 'Priya Sharma', 'student', '+1 (555) 456-7890'),
    ('usr-staff-1', 'staff@hostelsync.edu', 'staff123', 'David Miller', 'staff', '+1 (555) 890-1234')
ON CONFLICT (email) DO NOTHING;

INSERT INTO rooms (id, room_number, hostel_name, block, floor, capacity, type, status, amenities)
VALUES
    ('rm-101', 'A-101', 'Horizon Hall', 'Block A', 1, 2, 'Standard Double (Non-AC)', 'available', '["Wi-Fi", "Study Table", "Balcony"]'::jsonb),
    ('rm-204', 'A-204', 'Horizon Hall', 'Block A', 2, 2, 'Deluxe Double (AC)', 'full', '["AC", "Wi-Fi", "Attached Bath"]'::jsonb),
    ('rm-302', 'B-102', 'Pinnacle Tower', 'Block B', 1, 2, 'Standard Double (Non-AC)', 'partially_occupied', '["Wi-Fi", "Study Table"]'::jsonb)
ON CONFLICT (room_number) DO NOTHING;
