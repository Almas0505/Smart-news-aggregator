import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const newsApi = {
  // Get all news
  getNews: (params?: {
    page?: number;
    limit?: number;
    category?: string;
    source?: string;
  }) => api.get("/news", { params }),

  // Get single news
  getNewsById: (id: string) => api.get(`/news/${id}`),

  // Get trending news
  getTrending: () => api.get("/news/trending"),

  // Get recommended news
  getRecommended: () => api.get("/news/recommended"),

  // Search news
  searchNews: (query: string, params?: { page?: number; limit?: number }) =>
    api.post("/news/search", { query, ...params }),
};

export const categoriesApi = {
  // Get all categories
  getCategories: () => api.get("/categories"),

  // Get news by category
  getNewsByCategory: (categoryId: string, params?: { page?: number }) =>
    api.get(`/categories/${categoryId}/news`, { params }),
};

export const userApi = {
  // Get current user
  getMe: () => api.get("/users/me"),

  // Update profile
  updateProfile: (data: any) => api.put("/users/me", data),

  // Get bookmarks
  getBookmarks: () => api.get("/users/me/bookmarks"),

  // Add bookmark
  addBookmark: (newsId: string) => api.post("/users/me/bookmarks", { newsId }),

  // Remove bookmark
  removeBookmark: (newsId: string) =>
    api.delete(`/users/me/bookmarks/${newsId}`),

  // Get reading history
  getHistory: () => api.get("/users/me/history"),
};

export const authApi = {
  // Register
  register: (data: { email: string; password: string; fullName: string }) =>
    api.post("/auth/register", data),

  // Login
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),

  // Logout
  logout: () => api.post("/auth/logout"),

  // Refresh token
  refresh: () => api.post("/auth/refresh"),
};
