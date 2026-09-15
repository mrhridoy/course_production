export type UserRole = "admin" | "teacher" | "student";
export type CourseLevel = "beginner" | "intermediate" | "advanced";
export type EnrollmentStatus = "active" | "completed" | "cancelled";
export type PaymentMethod = "bkash" | "nagad" | "card" | "manual";
export type PaymentStatus = "pending" | "completed" | "failed" | "refunded";

export interface User {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role: UserRole;
  avatar: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
}

export interface Course {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  thumbnail_url: string | null;
  promo_video_url: string | null;
  price: number;
  duration_hours: number | null;
  level: CourseLevel;
  is_published: boolean;
  category: Category | null;
  teacher: User | null;
  created_at: string;
  updated_at: string | null;
}

export interface Enrollment {
  id: number;
  student_id: number;
  course_id: number;
  status: EnrollmentStatus;
  enrolled_at: string;
}

export interface Payment {
  id: number;
  student_id: number;
  course_id: number;
  enrollment_id: number | null;
  amount: number;
  currency: string;
  method: PaymentMethod;
  transaction_id: string | null;
  status: PaymentStatus;
  note: string | null;
  paid_at: string | null;
  created_at: string;
}

export interface AdminDashboardStats {
  total_users: number;
  total_students: number;
  total_teachers: number;
  total_courses: number;
  published_courses: number;
  total_enrollments: number;
  total_revenue: number;
  pending_payments: number;
}

export interface TeacherDashboardStats {
  total_courses: number;
  published_courses: number;
  total_enrollments: number;
  total_revenue: number;
}

export interface ApiError {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
}
