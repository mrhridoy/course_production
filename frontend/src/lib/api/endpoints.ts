export const endpoints = {
  auth: {
    register: "/auth/register",
    login: "/auth/login",
    refresh: "/auth/refresh",
    me: "/auth/me",
  },
  users: {
    list: "/users/",
    me: "/users/me",
    byId: (id: number) => `/users/${id}`,
    role: (id: number) => `/users/${id}/role`,
    toggleActive: (id: number) => `/users/${id}/toggle-active`,
  },
  categories: {
    list: "/categories/",
    byId: (id: number) => `/categories/${id}`,
  },
  courses: {
    list: "/courses/",
    listAll: "/courses/all",
    byId: (id: number) => `/courses/${id}`,
    thumbnail: (id: number) => `/courses/${id}/thumbnail`,
  },
  enrollments: {
    listAll: "/enrollments/",
    my: "/enrollments/my",
    byId: (id: number) => `/enrollments/${id}`,
  },
  payments: {
    listAll: "/payments/",
    my: "/payments/my",
    status: (id: number) => `/payments/${id}/status`,
  },
  dashboard: {
    admin: "/dashboard/",
    teacher: "/dashboard/teacher",
  },
} as const;
