import express, { Request, Response } from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(express.json());

// In-Memory Database initialized with rich production-like seed data
interface User {
  id: string;
  email: string;
  password_hash: string;
  full_name: string;
  role: 'student' | 'warden' | 'staff';
  phone: string;
  avatar_url?: string;
  created_at: string;
}

interface Student {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  enrollment_no: string;
  department: string;
  year_of_study: number;
  gender: string;
  emergency_contact: string;
  blood_group: string;
  room_id: string | null;
  hostel_name: string;
  created_at: string;
}

interface Staff {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  employee_id: string;
  specialization: string;
  phone: string;
  status: 'available' | 'busy' | 'off_duty';
}

interface Room {
  id: string;
  room_number: string;
  hostel_name: string;
  block: string;
  floor: number;
  capacity: number;
  type: string;
  status: 'available' | 'partially_occupied' | 'full' | 'maintenance';
  amenities: string[];
}

interface RoomAllocation {
  id: string;
  student_id: string;
  room_id: string;
  allocated_by: string;
  allocation_date: string;
  status: 'active' | 'vacated' | 'transferred';
  notes?: string;
}

interface Complaint {
  id: string;
  complaint_code: string;
  student_id: string;
  student_name: string;
  room_id: string;
  room_number: string;
  category: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'assigned' | 'in_progress' | 'resolved' | 'rejected';
  assigned_to: string | null; // staff_id
  assigned_to_name: string | null;
  assigned_at: string | null;
  resolved_at: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
}

interface Visitor {
  id: string;
  student_id: string;
  student_name: string;
  room_number: string;
  visitor_name: string;
  phone_number: string;
  relationship: string;
  visit_date: string;
  entry_time: string;
  expected_exit_time: string;
  actual_exit_time: string | null;
  purpose: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  approved_by: string | null;
  rejection_reason: string | null;
  created_at: string;
}

interface Notice {
  id: string;
  title: string;
  content: string;
  category: 'General' | 'Maintenance' | 'Rules & Regulations' | 'Events' | 'Emergency';
  priority: 'normal' | 'important' | 'urgent';
  target_audience: 'all' | 'students' | 'staff';
  published_by_name: string;
  is_published: boolean;
  created_at: string;
}

interface MessFeedback {
  id: string;
  student_id: string;
  student_name: string;
  meal_type: 'breakfast' | 'lunch' | 'snacks' | 'dinner';
  rating: number;
  hygiene_rating: number;
  taste_rating: number;
  comments: string;
  date: string;
  created_at: string;
}

interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

// Initial Seed Data
const users: User[] = [
  {
    id: 'usr-warden-1',
    email: 'warden@hostelsync.edu',
    password_hash: 'admin123',
    full_name: 'Dr. Robert Vance',
    role: 'warden',
    phone: '+1 (555) 234-5678',
    created_at: '2026-01-10T08:00:00Z',
  },
  {
    id: 'usr-student-1',
    email: 'student@hostelsync.edu',
    password_hash: 'student123',
    full_name: 'Alex Morgan',
    role: 'student',
    phone: '+1 (555) 345-6789',
    created_at: '2026-08-01T10:00:00Z',
  },
  {
    id: 'usr-student-2',
    email: 'priya@hostelsync.edu',
    password_hash: 'student123',
    full_name: 'Priya Sharma',
    role: 'student',
    phone: '+1 (555) 456-7890',
    created_at: '2026-08-01T10:30:00Z',
  },
  {
    id: 'usr-student-3',
    email: 'marcus@hostelsync.edu',
    password_hash: 'student123',
    full_name: 'Marcus Chen',
    role: 'student',
    phone: '+1 (555) 567-8901',
    created_at: '2026-08-02T11:00:00Z',
  },
  {
    id: 'usr-student-4',
    email: 'sarah@hostelsync.edu',
    password_hash: 'student123',
    full_name: 'Sarah Jenkins',
    role: 'student',
    phone: '+1 (555) 678-9012',
    created_at: '2026-08-02T11:30:00Z',
  },
  {
    id: 'usr-student-5',
    email: 'liam@hostelsync.edu',
    password_hash: 'student123',
    full_name: 'Liam O’Connor',
    role: 'student',
    phone: '+1 (555) 789-0123',
    created_at: '2026-08-03T09:00:00Z',
  },
  {
    id: 'usr-staff-1',
    email: 'staff@hostelsync.edu',
    password_hash: 'staff123',
    full_name: 'David Miller',
    role: 'staff',
    phone: '+1 (555) 890-1234',
    created_at: '2026-02-15T08:00:00Z',
  },
  {
    id: 'usr-staff-2',
    email: 'carlos@hostelsync.edu',
    password_hash: 'staff123',
    full_name: 'Carlos Mendez',
    role: 'staff',
    phone: '+1 (555) 901-2345',
    created_at: '2026-02-16T08:00:00Z',
  },
  {
    id: 'usr-staff-3',
    email: 'anita@hostelsync.edu',
    password_hash: 'staff123',
    full_name: 'Anita Roy',
    role: 'staff',
    phone: '+1 (555) 012-3456',
    created_at: '2026-03-01T08:00:00Z',
  }
];

const rooms: Room[] = [
  {
    id: 'rm-101',
    room_number: 'A-101',
    hostel_name: 'Horizon Hall',
    block: 'Block A',
    floor: 1,
    capacity: 2,
    type: 'Standard Double (Non-AC)',
    status: 'full',
    amenities: ['High-speed Wi-Fi', 'Study Tables', 'Attached Balcony', 'Wardrobes'],
  },
  {
    id: 'rm-102',
    room_number: 'A-102',
    hostel_name: 'Horizon Hall',
    block: 'Block A',
    floor: 1,
    capacity: 2,
    type: 'Standard Double (Non-AC)',
    status: 'partially_occupied',
    amenities: ['High-speed Wi-Fi', 'Study Tables', 'Attached Balcony'],
  },
  {
    id: 'rm-201',
    room_number: 'A-201',
    hostel_name: 'Horizon Hall',
    block: 'Block A',
    floor: 2,
    capacity: 3,
    type: 'Deluxe Triple (AC)',
    status: 'partially_occupied',
    amenities: ['Air Conditioning', 'High-speed Wi-Fi', 'Attached Bathroom', 'Smart Desk'],
  },
  {
    id: 'rm-204',
    room_number: 'A-204',
    hostel_name: 'Horizon Hall',
    block: 'Block A',
    floor: 2,
    capacity: 2,
    type: 'Deluxe Double (AC)',
    status: 'full',
    amenities: ['Air Conditioning', 'High-speed Wi-Fi', 'Attached Bathroom', 'Balcony'],
  },
  {
    id: 'rm-301',
    room_number: 'B-101',
    hostel_name: 'Pinnacle Tower',
    block: 'Block B',
    floor: 1,
    capacity: 2,
    type: 'Standard Double (Non-AC)',
    status: 'available',
    amenities: ['High-speed Wi-Fi', 'Study Tables', 'Ceiling Fan'],
  },
  {
    id: 'rm-302',
    room_number: 'B-102',
    hostel_name: 'Pinnacle Tower',
    block: 'Block B',
    floor: 1,
    capacity: 2,
    type: 'Standard Double (Non-AC)',
    status: 'partially_occupied',
    amenities: ['High-speed Wi-Fi', 'Study Tables', 'Garden View'],
  },
  {
    id: 'rm-303',
    room_number: 'B-201',
    hostel_name: 'Pinnacle Tower',
    block: 'Block B',
    floor: 2,
    capacity: 4,
    type: 'Dorm Quad (Non-AC)',
    status: 'maintenance',
    amenities: ['Wi-Fi', 'Lockers', 'Bunk Beds'],
  },
  {
    id: 'rm-304',
    room_number: 'B-202',
    hostel_name: 'Pinnacle Tower',
    block: 'Block B',
    floor: 2,
    capacity: 2,
    type: 'Deluxe Double (AC)',
    status: 'available',
    amenities: ['Air Conditioning', 'Wi-Fi', 'Attached Washroom'],
  }
];

const students: Student[] = [
  {
    id: 'std-1',
    user_id: 'usr-student-1',
    full_name: 'Alex Morgan',
    email: 'student@hostelsync.edu',
    enrollment_no: 'CS-2023-042',
    department: 'Computer Science & Engineering',
    year_of_study: 3,
    gender: 'Male',
    emergency_contact: '+1 (555) 987-6543 (Parent)',
    blood_group: 'O+',
    room_id: 'rm-204',
    hostel_name: 'Horizon Hall',
    created_at: '2026-08-01T10:00:00Z',
  },
  {
    id: 'std-2',
    user_id: 'usr-student-2',
    full_name: 'Priya Sharma',
    email: 'priya@hostelsync.edu',
    enrollment_no: 'EE-2024-118',
    department: 'Electrical Engineering',
    year_of_study: 2,
    gender: 'Female',
    emergency_contact: '+1 (555) 876-5432 (Guardian)',
    blood_group: 'B+',
    room_id: 'rm-302',
    hostel_name: 'Pinnacle Tower',
    created_at: '2026-08-01T10:30:00Z',
  },
  {
    id: 'std-3',
    user_id: 'usr-student-3',
    full_name: 'Marcus Chen',
    email: 'marcus@hostelsync.edu',
    enrollment_no: 'ME-2023-089',
    department: 'Mechanical Engineering',
    year_of_study: 3,
    gender: 'Male',
    emergency_contact: '+1 (555) 765-4321 (Parent)',
    blood_group: 'A+',
    room_id: 'rm-204', // Roommate of Alex!
    hostel_name: 'Horizon Hall',
    created_at: '2026-08-02T11:00:00Z',
  },
  {
    id: 'std-4',
    user_id: 'usr-student-4',
    full_name: 'Sarah Jenkins',
    email: 'sarah@hostelsync.edu',
    enrollment_no: 'BIO-2025-015',
    department: 'Biotechnology',
    year_of_study: 1,
    gender: 'Female',
    emergency_contact: '+1 (555) 654-3210 (Mother)',
    blood_group: 'AB+',
    room_id: 'rm-101',
    hostel_name: 'Horizon Hall',
    created_at: '2026-08-02T11:30:00Z',
  },
  {
    id: 'std-5',
    user_id: 'usr-student-5',
    full_name: 'Liam O’Connor',
    email: 'liam@hostelsync.edu',
    enrollment_no: 'CS-2024-077',
    department: 'Computer Science',
    year_of_study: 2,
    gender: 'Male',
    emergency_contact: '+1 (555) 543-2109 (Father)',
    blood_group: 'O-',
    room_id: 'rm-101', // Roommate of Sarah in rm-101
    hostel_name: 'Horizon Hall',
    created_at: '2026-08-03T09:00:00Z',
  },
];

const staffMembers: Staff[] = [
  {
    id: 'stf-1',
    user_id: 'usr-staff-1',
    full_name: 'David Miller',
    email: 'staff@hostelsync.edu',
    employee_id: 'EMP-ELEC-04',
    specialization: 'Electrical & AC Maintenance',
    phone: '+1 (555) 890-1234',
    status: 'available',
  },
  {
    id: 'stf-2',
    user_id: 'usr-staff-2',
    full_name: 'Carlos Mendez',
    email: 'carlos@hostelsync.edu',
    employee_id: 'EMP-PLUM-02',
    specialization: 'Plumbing & Drainage',
    phone: '+1 (555) 901-2345',
    status: 'busy',
  },
  {
    id: 'stf-3',
    user_id: 'usr-staff-3',
    full_name: 'Anita Roy',
    email: 'anita@hostelsync.edu',
    employee_id: 'EMP-CARP-08',
    specialization: 'Carpentry & Furniture',
    phone: '+1 (555) 012-3456',
    status: 'available',
  }
];

const allocations: RoomAllocation[] = [
  {
    id: 'alc-1',
    student_id: 'std-1',
    room_id: 'rm-204',
    allocated_by: 'usr-warden-1',
    allocation_date: '2026-08-10',
    status: 'active',
    notes: 'Allocated for Academic Year 2026-27',
  },
  {
    id: 'alc-2',
    student_id: 'std-3',
    room_id: 'rm-204',
    allocated_by: 'usr-warden-1',
    allocation_date: '2026-08-10',
    status: 'active',
    notes: 'Allocated for Academic Year 2026-27',
  },
  {
    id: 'alc-3',
    student_id: 'std-2',
    room_id: 'rm-302',
    allocated_by: 'usr-warden-1',
    allocation_date: '2026-08-12',
    status: 'active',
  },
  {
    id: 'alc-4',
    student_id: 'std-4',
    room_id: 'rm-101',
    allocated_by: 'usr-warden-1',
    allocation_date: '2026-08-15',
    status: 'active',
  },
  {
    id: 'alc-5',
    student_id: 'std-5',
    room_id: 'rm-101',
    allocated_by: 'usr-warden-1',
    allocation_date: '2026-08-15',
    status: 'active',
  },
];

const complaints: Complaint[] = [
  {
    id: 'cmp-1',
    complaint_code: 'CMP-2026-001',
    student_id: 'std-1',
    student_name: 'Alex Morgan',
    room_id: 'rm-204',
    room_number: 'A-204',
    category: 'Electrical',
    title: 'Ceiling fan making clicking noise on high speeds',
    description: 'The ceiling fan regulator vibrates heavily and produces clicking sound on speeds 4 and 5.',
    priority: 'medium',
    status: 'assigned',
    assigned_to: 'stf-1',
    assigned_to_name: 'David Miller',
    assigned_at: '2026-10-02T14:30:00Z',
    resolved_at: null,
    resolution_notes: null,
    created_at: '2026-10-02T10:15:00Z',
    updated_at: '2026-10-02T14:30:00Z',
  },
  {
    id: 'cmp-2',
    complaint_code: 'CMP-2026-002',
    student_id: 'std-2',
    student_name: 'Priya Sharma',
    room_id: 'rm-302',
    room_number: 'B-102',
    category: 'Plumbing',
    title: 'Water tap leaking continuously in washroom',
    description: 'Hot water faucet handle is loose and water drips approximately 2 liters per hour.',
    priority: 'high',
    status: 'in_progress',
    assigned_to: 'stf-2',
    assigned_to_name: 'Carlos Mendez',
    assigned_at: '2026-10-03T09:00:00Z',
    resolved_at: null,
    resolution_notes: 'Inspected washer. Sourcing 1/2-inch brass cartridge from central store.',
    created_at: '2026-10-03T08:00:00Z',
    updated_at: '2026-10-03T11:20:00Z',
  },
  {
    id: 'cmp-3',
    complaint_code: 'CMP-2026-003',
    student_id: 'std-3',
    student_name: 'Marcus Chen',
    room_id: 'rm-204',
    room_number: 'A-204',
    category: 'Wi-Fi/Internet',
    title: 'LAN port 2 connectivity intermittent',
    description: 'The RJ45 ethernet socket near desk 2 keeps dropping connection every 10 minutes.',
    priority: 'low',
    status: 'pending',
    assigned_to: null,
    assigned_to_name: null,
    assigned_at: null,
    resolved_at: null,
    resolution_notes: null,
    created_at: '2026-10-04T07:45:00Z',
    updated_at: '2026-10-04T07:45:00Z',
  },
  {
    id: 'cmp-4',
    complaint_code: 'CMP-2026-004',
    student_id: 'std-1',
    student_name: 'Alex Morgan',
    room_id: 'rm-204',
    room_number: 'A-204',
    category: 'Carpentry',
    title: 'Study wardrobe hinge loose',
    description: 'Right door hinge screws stripped out of the wooden frame.',
    priority: 'low',
    status: 'resolved',
    assigned_to: 'stf-3',
    assigned_to_name: 'Anita Roy',
    assigned_at: '2026-09-25T11:00:00Z',
    resolved_at: '2026-09-26T15:30:00Z',
    resolution_notes: 'Replaced hydraulic hinge with heavy duty stainless screws and tested alignment.',
    created_at: '2026-09-25T09:20:00Z',
    updated_at: '2026-09-26T15:30:00Z',
  }
];

const visitors: Visitor[] = [
  {
    id: 'vis-1',
    student_id: 'std-1',
    student_name: 'Alex Morgan',
    room_number: 'A-204',
    visitor_name: 'Thomas Morgan',
    phone_number: '+1 (555) 789-4321',
    relationship: 'Parent',
    visit_date: '2026-10-06',
    entry_time: '14:00',
    expected_exit_time: '18:00',
    actual_exit_time: null,
    purpose: 'Semester fee discussion and bringing winter clothes',
    status: 'approved',
    approved_by: 'usr-warden-1',
    rejection_reason: null,
    created_at: '2026-10-03T16:00:00Z',
  },
  {
    id: 'vis-2',
    student_id: 'std-2',
    student_name: 'Priya Sharma',
    room_number: 'B-102',
    visitor_name: 'Sunita Sharma',
    phone_number: '+1 (555) 890-5432',
    relationship: 'Mother',
    visit_date: '2026-10-07',
    entry_time: '11:00',
    expected_exit_time: '16:00',
    actual_exit_time: null,
    purpose: 'Family visit during festive weekend',
    status: 'pending',
    approved_by: null,
    rejection_reason: null,
    created_at: '2026-10-04T12:00:00Z',
  },
  {
    id: 'vis-3',
    student_id: 'std-3',
    student_name: 'Marcus Chen',
    room_number: 'A-204',
    visitor_name: 'Kevin Zhao',
    phone_number: '+1 (555) 901-6543',
    relationship: 'Friend',
    visit_date: '2026-10-01',
    entry_time: '16:00',
    expected_exit_time: '19:00',
    actual_exit_time: '18:45',
    purpose: 'Project collaboration',
    status: 'completed',
    approved_by: 'usr-warden-1',
    rejection_reason: null,
    created_at: '2026-09-30T10:00:00Z',
  }
];

const notices: Notice[] = [
  {
    id: 'not-1',
    title: 'Water Supply Maintenance Schedule - Blocks A & B',
    content: 'Routine overhead tank cleaning and chlorination will occur on Wednesday, 10:00 AM to 02:00 PM. Please store sufficient drinking water in advance.',
    category: 'Maintenance',
    priority: 'urgent',
    target_audience: 'all',
    published_by_name: 'Dr. Robert Vance (Chief Warden)',
    is_published: true,
    created_at: '2026-10-03T09:00:00Z',
  },
  {
    id: 'not-2',
    title: 'Hostel Night & Cultural Festival Registrations',
    content: 'Annual inter-hostel cultural competition entries are now open! Sign up at the warden office or through your floor representative before Oct 15.',
    category: 'Events',
    priority: 'normal',
    target_audience: 'students',
    published_by_name: 'Dr. Robert Vance (Chief Warden)',
    is_published: true,
    created_at: '2026-10-01T14:30:00Z',
  },
  {
    id: 'not-3',
    title: 'Strict Adherence to Night Curfew (10:30 PM)',
    content: 'All residents are reminded that main biometric gates lock at 10:30 PM sharp. Prior written gate passes are mandatory for late academic library passes.',
    category: 'Rules & Regulations',
    priority: 'important',
    target_audience: 'all',
    published_by_name: 'Hostel Administration',
    is_published: true,
    created_at: '2026-09-28T08:00:00Z',
  }
];

const messFeedbackList: MessFeedback[] = [
  {
    id: 'fb-1',
    student_id: 'std-1',
    student_name: 'Alex Morgan',
    meal_type: 'dinner',
    rating: 4,
    hygiene_rating: 5,
    taste_rating: 4,
    comments: 'Paneer butter masala and fresh rotis were great. Salad counter was well replenished.',
    date: '2026-10-03',
    created_at: '2026-10-03T21:10:00Z',
  },
  {
    id: 'fb-2',
    student_id: 'std-2',
    student_name: 'Priya Sharma',
    meal_type: 'breakfast',
    rating: 3,
    hygiene_rating: 4,
    taste_rating: 3,
    comments: 'Idlis were a bit cold by 8:30 AM. Sambhar tasted good.',
    date: '2026-10-04',
    created_at: '2026-10-04T09:05:00Z',
  },
  {
    id: 'fb-3',
    student_id: 'std-3',
    student_name: 'Marcus Chen',
    meal_type: 'lunch',
    rating: 5,
    hygiene_rating: 5,
    taste_rating: 5,
    comments: 'Excellent festive meal menu with sweet dessert!',
    date: '2026-10-02',
    created_at: '2026-10-02T13:45:00Z',
  }
];

const notifications: NotificationItem[] = [
  {
    id: 'ntf-1',
    user_id: 'usr-student-1',
    title: 'Complaint Assigned',
    message: 'Your complaint CMP-2026-001 has been assigned to David Miller (Electrical).',
    type: 'complaint_update',
    is_read: false,
    created_at: '2026-10-02T14:30:00Z',
  },
  {
    id: 'ntf-2',
    user_id: 'usr-student-1',
    title: 'Visitor Request Approved',
    message: 'Your visitor request for Thomas Morgan on 2026-10-06 has been approved by the Warden.',
    type: 'visitor_status',
    is_read: true,
    created_at: '2026-10-03T16:05:00Z',
  },
  {
    id: 'ntf-3',
    user_id: 'usr-staff-1',
    title: 'New Maintenance Task Assigned',
    message: 'New complaint CMP-2026-001 assigned to you: Ceiling fan issue in Room A-204.',
    type: 'complaint_update',
    is_read: false,
    created_at: '2026-10-02T14:30:00Z',
  },
  {
    id: 'ntf-4',
    user_id: 'usr-warden-1',
    title: 'New Visitor Request Pending',
    message: 'Priya Sharma registered a visitor request for Sunita Sharma.',
    type: 'visitor_status',
    is_read: false,
    created_at: '2026-10-04T12:00:00Z',
  }
];

// Helper to update room status based on occupants
function updateRoomStatus(roomId: string) {
  const room = rooms.find(r => r.id === roomId);
  if (!room) return;
  const occupants = students.filter(s => s.room_id === roomId).length;
  if (occupants === 0) {
    if (room.status !== 'maintenance') room.status = 'available';
  } else if (occupants >= room.capacity) {
    room.status = 'full';
  } else {
    room.status = 'partially_occupied';
  }
}

// ---------------- REST API ROUTES ----------------

// AUTHENTICATION
app.post('/api/auth/login', (req: Request, res: Response) => {
  const { email, password } = req.body;
  const user = users.find(u => u.email.toLowerCase() === (email || '').toLowerCase().trim());

  if (!user || user.password_hash !== password) {
    return res.status(401).json({ message: 'Invalid email or password' });
  }

  // Find linked profile
  let studentProfile = null;
  let staffProfile = null;

  if (user.role === 'student') {
    studentProfile = students.find(s => s.user_id === user.id) || null;
  } else if (user.role === 'staff') {
    staffProfile = staffMembers.find(st => st.user_id === user.id) || null;
  }

  const token = `token-${user.id}-${Date.now()}`;
  return res.json({
    token,
    user: {
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      phone: user.phone,
    },
    studentProfile,
    staffProfile,
  });
});

app.post('/api/auth/register', (req: Request, res: Response) => {
  const { full_name, email, password, role, phone, enrollment_no, department, year_of_study, gender } = req.body;

  if (!email || !password || !full_name) {
    return res.status(400).json({ message: 'Missing required registration fields' });
  }

  if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
    return res.status(400).json({ message: 'User with this email already exists' });
  }

  const userRole = role === 'staff' ? 'staff' : (role === 'warden' ? 'warden' : 'student');
  const userId = `usr-${Date.now()}`;

  const newUser: User = {
    id: userId,
    email: email.toLowerCase().trim(),
    password_hash: password,
    full_name,
    role: userRole,
    phone: phone || '',
    created_at: new Date().toISOString(),
  };
  users.push(newUser);

  let newStudentProfile = null;
  if (userRole === 'student') {
    newStudentProfile = {
      id: `std-${Date.now()}`,
      user_id: userId,
      full_name,
      email: newUser.email,
      enrollment_no: enrollment_no || `ST-${Math.floor(1000 + Math.random() * 9000)}`,
      department: department || 'Engineering',
      year_of_study: Number(year_of_study) || 1,
      gender: gender || 'Other',
      emergency_contact: '',
      blood_group: 'Unknown',
      room_id: null,
      hostel_name: 'Horizon Hall',
      created_at: new Date().toISOString(),
    };
    students.push(newStudentProfile);
  }

  const token = `token-${newUser.id}-${Date.now()}`;
  return res.status(201).json({
    message: 'Registration successful',
    token,
    user: {
      id: newUser.id,
      email: newUser.email,
      full_name: newUser.full_name,
      role: newUser.role,
      phone: newUser.phone,
    },
    studentProfile: newStudentProfile,
  });
});

app.post('/api/auth/logout', (_req: Request, res: Response) => {
  return res.json({ message: 'Logged out successfully' });
});

app.post('/api/auth/forgot-password', (req: Request, res: Response) => {
  const { email } = req.body;
  const user = users.find(u => u.email.toLowerCase() === (email || '').toLowerCase());
  if (!user) {
    return res.status(404).json({ message: 'No account found with this email address' });
  }
  return res.json({ message: 'Password reset link sent to your registered email' });
});

app.post('/api/auth/reset-password', (req: Request, res: Response) => {
  const { email, new_password } = req.body;
  const user = users.find(u => u.email.toLowerCase() === (email || '').toLowerCase());
  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }
  user.password_hash = new_password;
  return res.json({ message: 'Password has been reset successfully' });
});

// STUDENTS
app.get('/api/students', (_req: Request, res: Response) => {
  const result = students.map(s => {
    const room = rooms.find(r => r.id === s.room_id);
    const roommates = s.room_id ? students.filter(r => r.room_id === s.room_id && r.id !== s.id) : [];
    return {
      ...s,
      room_number: room ? room.room_number : null,
      block: room ? room.block : null,
      floor: room ? room.floor : null,
      roommates_count: roommates.length,
    };
  });
  return res.json(result);
});

app.get('/api/students/:id', (req: Request, res: Response) => {
  const student = students.find(s => s.id === req.params.id || s.user_id === req.params.id);
  if (!student) return res.status(404).json({ message: 'Student not found' });

  const room = rooms.find(r => r.id === student.room_id);
  const roommates = student.room_id
    ? students
        .filter(r => r.room_id === student.room_id && r.id !== student.id)
        .map(rm => ({
          id: rm.id,
          full_name: rm.full_name,
          email: rm.email,
          enrollment_no: rm.enrollment_no,
          department: rm.department,
          year_of_study: rm.year_of_study,
        }))
    : [];

  return res.json({
    ...student,
    room: room
      ? {
          ...room,
          current_occupants: students.filter(st => st.room_id === room.id).length,
        }
      : null,
    roommates,
  });
});

app.put('/api/students/:id', (req: Request, res: Response) => {
  const student = students.find(s => s.id === req.params.id || s.user_id === req.params.id);
  if (!student) return res.status(404).json({ message: 'Student not found' });

  const { full_name, emergency_contact, blood_group, department, year_of_study, phone } = req.body;
  if (full_name) {
    student.full_name = full_name;
    const user = users.find(u => u.id === student.user_id);
    if (user) user.full_name = full_name;
  }
  if (emergency_contact !== undefined) student.emergency_contact = emergency_contact;
  if (blood_group !== undefined) student.blood_group = blood_group;
  if (department !== undefined) student.department = department;
  if (year_of_study !== undefined) student.year_of_study = Number(year_of_study);
  if (phone) {
    const user = users.find(u => u.id === student.user_id);
    if (user) user.phone = phone;
  }

  return res.json({ message: 'Student updated successfully', student });
});

// ROOMS
app.get('/api/rooms', (req: Request, res: Response) => {
  const { block, floor, status } = req.query;
  let filtered = rooms.map(r => {
    const occupants = students.filter(s => s.room_id === r.id);
    return {
      ...r,
      current_occupants: occupants.length,
      occupants: occupants.map(o => ({
        id: o.id,
        full_name: o.full_name,
        enrollment_no: o.enrollment_no,
        department: o.department,
      })),
    };
  });

  if (block) {
    filtered = filtered.filter(r => r.block === block);
  }
  if (floor) {
    filtered = filtered.filter(r => r.floor === Number(floor));
  }
  if (status) {
    filtered = filtered.filter(r => r.status === status);
  }

  return res.json(filtered);
});

app.post('/api/rooms', (req: Request, res: Response) => {
  const { room_number, hostel_name, block, floor, capacity, type, amenities } = req.body;
  if (!room_number || !capacity) {
    return res.status(400).json({ message: 'Room number and capacity are required' });
  }

  if (rooms.some(r => r.room_number.toLowerCase() === room_number.toLowerCase())) {
    return res.status(400).json({ message: 'Room number already exists' });
  }

  const newRoom: Room = {
    id: `rm-${Date.now()}`,
    room_number,
    hostel_name: hostel_name || 'Horizon Hall',
    block: block || 'Block A',
    floor: Number(floor) || 1,
    capacity: Number(capacity) || 2,
    type: type || 'Standard Double',
    status: 'available',
    amenities: amenities || ['High-speed Wi-Fi', 'Study Table'],
  };

  rooms.push(newRoom);
  return res.status(201).json(newRoom);
});

app.put('/api/rooms/:id', (req: Request, res: Response) => {
  const room = rooms.find(r => r.id === req.params.id);
  if (!room) return res.status(404).json({ message: 'Room not found' });

  const { room_number, hostel_name, block, floor, capacity, type, status, amenities } = req.body;
  if (room_number) room.room_number = room_number;
  if (hostel_name) room.hostel_name = hostel_name;
  if (block) room.block = block;
  if (floor !== undefined) room.floor = Number(floor);
  if (capacity !== undefined) room.capacity = Number(capacity);
  if (type) room.type = type;
  if (status) room.status = status;
  if (amenities) room.amenities = amenities;

  updateRoomStatus(room.id);
  return res.json(room);
});

app.delete('/api/rooms/:id', (req: Request, res: Response) => {
  const index = rooms.findIndex(r => r.id === req.params.id);
  if (index === -1) return res.status(404).json({ message: 'Room not found' });

  // Unassign any students from this room
  students.forEach(s => {
    if (s.room_id === req.params.id) {
      s.room_id = null;
    }
  });

  rooms.splice(index, 1);
  return res.json({ message: 'Room deleted successfully' });
});

// ROOM ALLOCATIONS
app.post('/api/allocations', (req: Request, res: Response) => {
  const { student_id, room_id, allocated_by, notes } = req.body;
  const student = students.find(s => s.id === student_id);
  const room = rooms.find(r => r.id === room_id);

  if (!student || !room) {
    return res.status(400).json({ message: 'Invalid student or room ID' });
  }

  const currentOccupants = students.filter(s => s.room_id === room_id).length;
  if (currentOccupants >= room.capacity) {
    return res.status(400).json({ message: 'Room is already at full capacity' });
  }

  // Remove old allocation if exists
  const oldRoomId = student.room_id;
  student.room_id = room.id;

  const newAllocation: RoomAllocation = {
    id: `alc-${Date.now()}`,
    student_id: student.id,
    room_id: room.id,
    allocated_by: allocated_by || 'usr-warden-1',
    allocation_date: new Date().toISOString().split('T')[0],
    status: 'active',
    notes,
  };
  allocations.push(newAllocation);

  updateRoomStatus(room.id);
  if (oldRoomId && oldRoomId !== room.id) {
    updateRoomStatus(oldRoomId);
  }

  // Create notification
  notifications.push({
    id: `ntf-${Date.now()}`,
    user_id: student.user_id,
    title: 'Room Allocated',
    message: `You have been allocated Room ${room.room_number} (${room.hostel_name}, ${room.block}).`,
    type: 'room_allocation',
    is_read: false,
    created_at: new Date().toISOString(),
  });

  return res.status(201).json({ message: 'Student allocated to room successfully', allocation: newAllocation });
});

app.delete('/api/allocations/:studentId', (req: Request, res: Response) => {
  const student = students.find(s => s.id === req.params.studentId);
  if (!student) return res.status(404).json({ message: 'Student not found' });

  const oldRoomId = student.room_id;
  student.room_id = null;

  if (oldRoomId) {
    updateRoomStatus(oldRoomId);
  }

  // Update allocation records
  const activeAlloc = allocations.find(a => a.student_id === student.id && a.status === 'active');
  if (activeAlloc) {
    activeAlloc.status = 'vacated';
  }

  notifications.push({
    id: `ntf-${Date.now()}`,
    user_id: student.user_id,
    title: 'Room De-allocated',
    message: 'Your hostel room allocation has been vacated.',
    type: 'room_allocation',
    is_read: false,
    created_at: new Date().toISOString(),
  });

  return res.json({ message: 'Student room allocation removed successfully' });
});

// COMPLAINTS
app.get('/api/complaints', (req: Request, res: Response) => {
  const { student_id, staff_id, status, category, priority } = req.query;
  let list = [...complaints];

  if (student_id) {
    list = list.filter(c => c.student_id === student_id);
  }
  if (staff_id) {
    list = list.filter(c => c.assigned_to === staff_id);
  }
  if (status) {
    list = list.filter(c => c.status === status);
  }
  if (category) {
    list = list.filter(c => c.category.toLowerCase() === (category as string).toLowerCase());
  }
  if (priority) {
    list = list.filter(c => c.priority === priority);
  }

  // Sort newest first
  list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return res.json(list);
});

app.post('/api/complaints', (req: Request, res: Response) => {
  const { student_id, category, title, description, priority } = req.body;
  const student = students.find(s => s.id === student_id || s.user_id === student_id);

  if (!student) {
    return res.status(400).json({ message: 'Student profile not found' });
  }

  const room = rooms.find(r => r.id === student.room_id);
  const complaintCount = complaints.length + 1;
  const complaintCode = `CMP-2026-${String(complaintCount).padStart(3, '0')}`;

  const newComplaint: Complaint = {
    id: `cmp-${Date.now()}`,
    complaint_code: complaintCode,
    student_id: student.id,
    student_name: student.full_name,
    room_id: student.room_id || 'unallocated',
    room_number: room ? room.room_number : 'N/A',
    category: category || 'Other',
    title: title || 'Maintenance Request',
    description: description || '',
    priority: priority || 'medium',
    status: 'pending',
    assigned_to: null,
    assigned_to_name: null,
    assigned_at: null,
    resolved_at: null,
    resolution_notes: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  complaints.unshift(newComplaint);

  // Notify wardens
  const wardenUser = users.find(u => u.role === 'warden');
  if (wardenUser) {
    notifications.push({
      id: `ntf-${Date.now()}`,
      user_id: wardenUser.id,
      title: 'New Complaint Submitted',
      message: `${student.full_name} (${room ? room.room_number : 'Room Unassigned'}) submitted: ${newComplaint.title}`,
      type: 'complaint_update',
      is_read: false,
      created_at: new Date().toISOString(),
    });
  }

  return res.status(201).json(newComplaint);
});

app.get('/api/complaints/:id', (req: Request, res: Response) => {
  const complaint = complaints.find(c => c.id === req.params.id);
  if (!complaint) return res.status(404).json({ message: 'Complaint not found' });
  return res.json(complaint);
});

app.put('/api/complaints/:id', (req: Request, res: Response) => {
  const complaint = complaints.find(c => c.id === req.params.id);
  if (!complaint) return res.status(404).json({ message: 'Complaint not found' });

  const { status, assigned_to, resolution_notes, priority } = req.body;

  if (priority) {
    complaint.priority = priority;
  }

  if (assigned_to !== undefined) {
    if (assigned_to === null || assigned_to === '') {
      complaint.assigned_to = null;
      complaint.assigned_to_name = null;
      complaint.assigned_at = null;
      if (complaint.status === 'assigned') complaint.status = 'pending';
    } else {
      const staff = staffMembers.find(st => st.id === assigned_to || st.user_id === assigned_to);
      if (staff) {
        complaint.assigned_to = staff.id;
        complaint.assigned_to_name = staff.full_name;
        complaint.assigned_at = new Date().toISOString();
        if (complaint.status === 'pending') {
          complaint.status = 'assigned';
        }
        // Notify staff member
        notifications.push({
          id: `ntf-${Date.now()}-stf`,
          user_id: staff.user_id,
          title: 'Task Assigned',
          message: `Complaint ${complaint.complaint_code} (${complaint.category}) in ${complaint.room_number} assigned to you.`,
          type: 'complaint_update',
          is_read: false,
          created_at: new Date().toISOString(),
        });
      }
    }
  }

  if (status) {
    complaint.status = status;
    if (status === 'resolved') {
      complaint.resolved_at = new Date().toISOString();
    }
  }

  if (resolution_notes !== undefined) {
    complaint.resolution_notes = resolution_notes;
  }

  complaint.updated_at = new Date().toISOString();

  // Notify student
  const student = students.find(s => s.id === complaint.student_id);
  if (student) {
    notifications.push({
      id: `ntf-${Date.now()}-std`,
      user_id: student.user_id,
      title: `Complaint Status: ${complaint.status.toUpperCase()}`,
      message: `Your complaint ${complaint.complaint_code} is now ${complaint.status}. ${resolution_notes ? 'Note: ' + resolution_notes : ''}`,
      type: 'complaint_update',
      is_read: false,
      created_at: new Date().toISOString(),
    });
  }

  return res.json(complaint);
});

// STAFF
app.get('/api/staff', (_req: Request, res: Response) => {
  const result = staffMembers.map(st => {
    const assignedTasks = complaints.filter(c => c.assigned_to === st.id);
    const activeTasks = assignedTasks.filter(c => c.status === 'assigned' || c.status === 'in_progress');
    const resolvedTasks = assignedTasks.filter(c => c.status === 'resolved');
    return {
      ...st,
      active_tasks_count: activeTasks.length,
      resolved_tasks_count: resolvedTasks.length,
    };
  });
  return res.json(result);
});

// VISITORS
app.get('/api/visitors', (req: Request, res: Response) => {
  const { student_id, status } = req.query;
  let list = [...visitors];

  if (student_id) {
    list = list.filter(v => v.student_id === student_id);
  }
  if (status) {
    list = list.filter(v => v.status === status);
  }

  list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return res.json(list);
});

app.post('/api/visitors', (req: Request, res: Response) => {
  const {
    student_id,
    visitor_name,
    phone_number,
    relationship,
    visit_date,
    entry_time,
    expected_exit_time,
    purpose,
  } = req.body;

  const student = students.find(s => s.id === student_id || s.user_id === student_id);
  if (!student) {
    return res.status(400).json({ message: 'Student not found' });
  }

  const room = rooms.find(r => r.id === student.room_id);

  const newVisitor: Visitor = {
    id: `vis-${Date.now()}`,
    student_id: student.id,
    student_name: student.full_name,
    room_number: room ? room.room_number : 'N/A',
    visitor_name,
    phone_number,
    relationship: relationship || 'Family',
    visit_date,
    entry_time,
    expected_exit_time,
    actual_exit_time: null,
    purpose: purpose || 'Visit',
    status: 'pending',
    approved_by: null,
    rejection_reason: null,
    created_at: new Date().toISOString(),
  };

  visitors.unshift(newVisitor);

  // Notify Warden
  const warden = users.find(u => u.role === 'warden');
  if (warden) {
    notifications.push({
      id: `ntf-${Date.now()}-vis`,
      user_id: warden.id,
      title: 'Visitor Approval Request',
      message: `${student.full_name} registered visitor ${newVisitor.visitor_name} for ${newVisitor.visit_date}.`,
      type: 'visitor_status',
      is_read: false,
      created_at: new Date().toISOString(),
    });
  }

  return res.status(201).json(newVisitor);
});

app.put('/api/visitors/:id', (req: Request, res: Response) => {
  const visitor = visitors.find(v => v.id === req.params.id);
  if (!visitor) return res.status(404).json({ message: 'Visitor entry not found' });

  const { status, rejection_reason, approved_by, actual_exit_time } = req.body;
  if (status) visitor.status = status;
  if (rejection_reason !== undefined) visitor.rejection_reason = rejection_reason;
  if (approved_by) visitor.approved_by = approved_by;
  if (actual_exit_time) visitor.actual_exit_time = actual_exit_time;

  // Notify student
  const student = students.find(s => s.id === visitor.student_id);
  if (student && status) {
    notifications.push({
      id: `ntf-${Date.now()}-visres`,
      user_id: student.user_id,
      title: `Visitor Request ${status.toUpperCase()}`,
      message: `Your visitor request for ${visitor.visitor_name} on ${visitor.visit_date} has been ${status}.`,
      type: 'visitor_status',
      is_read: false,
      created_at: new Date().toISOString(),
    });
  }

  return res.json(visitor);
});

// NOTICES
app.get('/api/notices', (_req: Request, res: Response) => {
  const list = [...notices].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  return res.json(list);
});

app.post('/api/notices', (req: Request, res: Response) => {
  const { title, content, category, priority, target_audience, published_by_name } = req.body;
  if (!title || !content) {
    return res.status(400).json({ message: 'Title and content are required' });
  }

  const newNotice: Notice = {
    id: `not-${Date.now()}`,
    title,
    content,
    category: category || 'General',
    priority: priority || 'normal',
    target_audience: target_audience || 'all',
    published_by_name: published_by_name || 'Hostel Warden Office',
    is_published: true,
    created_at: new Date().toISOString(),
  };

  notices.unshift(newNotice);

  // Broadcast notification to all active students
  students.forEach(st => {
    notifications.push({
      id: `ntf-${Date.now()}-${st.id}`,
      user_id: st.user_id,
      title: `Notice: ${newNotice.title}`,
      message: newNotice.content.substring(0, 100) + '...',
      type: 'notice',
      is_read: false,
      created_at: new Date().toISOString(),
    });
  });

  return res.status(201).json(newNotice);
});

app.put('/api/notices/:id', (req: Request, res: Response) => {
  const notice = notices.find(n => n.id === req.params.id);
  if (!notice) return res.status(404).json({ message: 'Notice not found' });

  const { title, content, category, priority, target_audience, is_published } = req.body;
  if (title) notice.title = title;
  if (content) notice.content = content;
  if (category) notice.category = category;
  if (priority) notice.priority = priority;
  if (target_audience) notice.target_audience = target_audience;
  if (is_published !== undefined) notice.is_published = is_published;

  return res.json(notice);
});

app.delete('/api/notices/:id', (req: Request, res: Response) => {
  const index = notices.findIndex(n => n.id === req.params.id);
  if (index === -1) return res.status(404).json({ message: 'Notice not found' });
  notices.splice(index, 1);
  return res.json({ message: 'Notice deleted successfully' });
});

// MESS FEEDBACK
app.get('/api/feedback', (_req: Request, res: Response) => {
  const list = [...messFeedbackList].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  return res.json(list);
});

app.post('/api/feedback', (req: Request, res: Response) => {
  const { student_id, meal_type, rating, hygiene_rating, taste_rating, comments, date } = req.body;
  const student = students.find(s => s.id === student_id || s.user_id === student_id);

  const newFeedback: MessFeedback = {
    id: `fb-${Date.now()}`,
    student_id: student ? student.id : (student_id || 'anonymous'),
    student_name: student ? student.full_name : 'Student',
    meal_type: meal_type || 'lunch',
    rating: Number(rating) || 4,
    hygiene_rating: Number(hygiene_rating) || 4,
    taste_rating: Number(taste_rating) || 4,
    comments: comments || '',
    date: date || new Date().toISOString().split('T')[0],
    created_at: new Date().toISOString(),
  };

  messFeedbackList.unshift(newFeedback);
  return res.status(201).json(newFeedback);
});

// NOTIFICATIONS
app.get('/api/notifications', (req: Request, res: Response) => {
  const { user_id } = req.query;
  let list = [...notifications];
  if (user_id) {
    list = list.filter(n => n.user_id === user_id);
  }
  list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return res.json(list);
});

app.put('/api/notifications/:id/read', (req: Request, res: Response) => {
  const notif = notifications.find(n => n.id === req.params.id);
  if (notif) notif.is_read = true;
  return res.json({ success: true });
});

// ANALYTICS ENDPOINTS
app.get('/api/analytics/rooms', (_req: Request, res: Response) => {
  const totalRooms = rooms.length;
  const occupiedRooms = rooms.filter(r => r.status === 'full').length;
  const partiallyOccupiedRooms = rooms.filter(r => r.status === 'partially_occupied').length;
  const availableRooms = rooms.filter(r => r.status === 'available').length;
  const maintenanceRooms = rooms.filter(r => r.status === 'maintenance').length;

  const totalCapacity = rooms.reduce((acc, r) => acc + r.capacity, 0);
  const currentStudents = students.filter(s => s.room_id !== null).length;
  const occupancyPercentage = totalCapacity > 0 ? Math.round((currentStudents / totalCapacity) * 100) : 0;

  // Breakdown by Block
  const blocksMap: { [key: string]: { total: number; occupied: number; capacity: number; students: number } } = {};
  rooms.forEach(r => {
    if (!blocksMap[r.block]) {
      blocksMap[r.block] = { total: 0, occupied: 0, capacity: 0, students: 0 };
    }
    blocksMap[r.block].total += 1;
    blocksMap[r.block].capacity += r.capacity;
    const occ = students.filter(s => s.room_id === r.id).length;
    blocksMap[r.block].students += occ;
    if (r.status === 'full') blocksMap[r.block].occupied += 1;
  });

  const blockBreakdown = Object.keys(blocksMap).map(block => ({
    name: block,
    totalRooms: blocksMap[block].total,
    capacity: blocksMap[block].capacity,
    currentStudents: blocksMap[block].students,
    occupancyRate: Math.round((blocksMap[block].students / (blocksMap[block].capacity || 1)) * 100),
  }));

  return res.json({
    totalRooms,
    occupiedRooms,
    partiallyOccupiedRooms,
    availableRooms,
    maintenanceRooms,
    totalCapacity,
    totalStudents: students.length,
    allocatedStudents: currentStudents,
    unallocatedStudents: students.length - currentStudents,
    occupancyPercentage,
    blockBreakdown,
  });
});

app.get('/api/analytics/complaints', (_req: Request, res: Response) => {
  const totalComplaints = complaints.length;
  const pendingComplaints = complaints.filter(c => c.status === 'pending').length;
  const assignedComplaints = complaints.filter(c => c.status === 'assigned').length;
  const inProgressComplaints = complaints.filter(c => c.status === 'in_progress').length;
  const resolvedComplaints = complaints.filter(c => c.status === 'resolved').length;
  const rejectedComplaints = complaints.filter(c => c.status === 'rejected').length;

  // Complaints by category
  const categoryMap: { [key: string]: number } = {};
  complaints.forEach(c => {
    categoryMap[c.category] = (categoryMap[c.category] || 0) + 1;
  });
  const byCategory = Object.keys(categoryMap).map(k => ({
    category: k,
    count: categoryMap[k],
  }));

  // Complaints by priority
  const priorityMap = {
    low: complaints.filter(c => c.priority === 'low').length,
    medium: complaints.filter(c => c.priority === 'medium').length,
    high: complaints.filter(c => c.priority === 'high').length,
    urgent: complaints.filter(c => c.priority === 'urgent').length,
  };

  return res.json({
    totalComplaints,
    pendingComplaints,
    assignedComplaints,
    inProgressComplaints,
    resolvedComplaints,
    rejectedComplaints,
    averageResolutionHours: 18.5,
    byCategory,
    priorityBreakdown: priorityMap,
  });
});

app.get('/api/analytics/maintenance', (_req: Request, res: Response) => {
  const staffTaskStats = staffMembers.map(st => {
    const assigned = complaints.filter(c => c.assigned_to === st.id);
    const resolved = assigned.filter(c => c.status === 'resolved');
    const pending = assigned.filter(c => c.status === 'assigned' || c.status === 'in_progress');
    return {
      staffId: st.id,
      staffName: st.full_name,
      specialization: st.specialization,
      tasksAssigned: assigned.length,
      tasksCompleted: resolved.length,
      tasksPending: pending.length,
      efficiencyRate: assigned.length > 0 ? Math.round((resolved.length / assigned.length) * 100) : 100,
    };
  });

  return res.json({
    totalAssignedTasks: complaints.filter(c => c.assigned_to !== null).length,
    totalCompletedTasks: complaints.filter(c => c.status === 'resolved').length,
    totalPendingTasks: complaints.filter(c => c.status === 'assigned' || c.status === 'in_progress').length,
    averageResponseHours: 3.2,
    staffTaskStats,
  });
});

// Setup Vite middleware in dev or static files in production
async function startServer() {
  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.resolve(__dirname, 'dist');
    if (fs.existsSync(distPath)) {
      app.use(express.static(distPath));
      app.get('*', (_req, res) => {
        res.sendFile(path.resolve(distPath, 'index.html'));
      });
    }
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`HostelSync Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
