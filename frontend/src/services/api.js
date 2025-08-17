import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const getToken = () => localStorage.getItem('token');
const setToken = (token) => localStorage.setItem('token', token);
const removeToken = () => localStorage.removeItem('token');

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (email, password) => api.post('/auth/login', { email, password }),
  verifyEmail: (token) => api.get(`/auth/verify-email?token=${token}`),
  getMe: () => api.get('/auth/me'),
};

// Users API
export const usersAPI = {
  getUsers: () => api.get('/users'),
  getUser: (userId) => api.get(`/users/${userId}`),
  getUserAchievements: (userId) => api.get(`/users/${userId}/achievements`),
};

// Classes API
export const classesAPI = {
  getClasses: () => api.get('/classes'),
  createClass: (classData) => api.post('/classes', classData),
  joinClass: (classId, classCode) => api.post(`/classes/${classId}/join`, { class_code: classCode }),
};

// Lessons API
export const lessonsAPI = {
  getLessons: (difficulty = null) => {
    const params = difficulty ? { difficulty } : {};
    return api.get('/lessons', { params });
  },
  getLesson: (lessonId) => api.get(`/lessons/${lessonId}`),
  createLesson: (lessonData) => api.post('/lessons', lessonData),
  startLesson: (lessonId) => api.post(`/lessons/${lessonId}/progress`),
  completeLesson: (lessonId) => api.put(`/lessons/${lessonId}/complete`),
};

// Quizzes API
export const quizzesAPI = {
  getLessonQuizzes: (lessonId) => api.get(`/lessons/${lessonId}/quizzes`),
  createQuiz: (quizData) => api.post('/quizzes', quizData),
  startQuizAttempt: (quizId) => api.post(`/quizzes/${quizId}/attempt`),
};

// Utility functions
export { getToken, setToken, removeToken };

export default api;