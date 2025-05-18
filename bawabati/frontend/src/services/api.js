import axios from 'axios';

// Use environment variable or fallback to default URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for cookies/CSRF
});

// Fetch and Set CSRF Token Automatically
const fetchAndSetCSRFToken = async () => {
    try {
        const response = await api.get('/csrf/', { withCredentials: true });
        const csrfToken = response.data?.csrfToken;
        if (csrfToken) {
            api.defaults.headers.common['X-CSRFToken'] = csrfToken;
            document.cookie = `csrftoken=${csrfToken}; path=/`;
        }
    } catch (error) {
        console.error("Failed to fetch CSRF Token:", error);
    }
};

// Fetch CSRF Token on Initialization
fetchAndSetCSRFToken();

// Add Axios Interceptors
api.interceptors.request.use(
    (config) => {
        const csrfToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const status = error.response?.status;
        if (status === 401) {
            localStorage.removeItem('user');
            window.location.href = '/login';
        } else if (status === 403) {
            // Refresh CSRF token automatically if expired
            await fetchAndSetCSRFToken();
        }
        return Promise.reject(error);
    }
);

// API Endpoints Organized by Resource
const apiEndpoints = {
    user: {
        getCurrentUser: () => api.get('/current-user/'),
        getUsers: () => api.get('/users/'),
        getUser: (id) => api.get(`/users/${id}/`),
        updateUser: (id, data) => api.put(`/users/${id}/`, data),
        deleteUser: (id) => api.delete(`/users/${id}/`),
    },
    auth: {
        login: (credentials) => api.post('/login/', credentials),
        register: (userData) => api.post('/register/', userData),
        logout: () => api.post('/logout/'),
        getCSRFToken: () => api.get('/csrf/'),
    },
    course: {
        getCourses: () => api.get('/courses/'),
        getCourse: (id) => api.get(`/courses/${id}/`),
        createCourse: (data) => api.post('/courses/', data),
        updateCourse: (id, data) => api.put(`/courses/${id}/`, data),
        deleteCourse: (id) => api.delete(`/courses/${id}/`),
    },
    enrollment: {
        getEnrollments: () => api.get('/enrollments/'),
        getEnrollment: (id) => api.get(`/enrollments/${id}/`),
        createEnrollment: (data) => api.post('/enrollments/', data),
        updateEnrollment: (id, data) => api.put(`/enrollments/${id}/`, data),
        deleteEnrollment: (id) => api.delete(`/enrollments/${id}/`),
    },
    dashboard: {
        getStats: () => api.get('/dashboard-stats/'),
    },
    student: {
        getStudents: () => api.get('/students/'),
        getStudent: (id) => api.get(`/students/${id}/`),
        createStudent: (data) => api.post('/students/', data),
        updateStudent: (id, data) => api.put(`/students/${id}/`, data),
        deleteStudent: (id) => api.delete(`/students/${id}/`),
    },
};

export { api, apiEndpoints };
