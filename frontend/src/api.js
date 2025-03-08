import axios from 'axios';

// Use environment variable for API URL or fallback to localhost for development
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
});

// Add a request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return api.post('/token', formData);
  },
  
  register: async (userData) => {
    return api.post('/users/', userData);
  },
  
  getCurrentUser: async () => {
    return api.get('/users/me');
  },
  
  updateProfile: async (profileData) => {
    return api.put('/users/me', profileData);
  },
  
  saveEvent: async (eventId) => {
    return api.post(`/users/me/save-event/${eventId}`);
  },
  
  saveOpportunity: async (opportunityId) => {
    return api.post(`/users/me/save-opportunity/${opportunityId}`);
  }
};

// Events services
export const eventService = {
  getEvents: async () => {
    return api.get('/events/');
  },
  
  createEvent: async (eventData) => {
    return api.post('/events/', eventData);
  },
  
  updateEvent: async (eventId, eventData) => {
    return api.put(`/events/${eventId}`, eventData);
  },
  
  deleteEvent: async (eventId) => {
    return api.delete(`/events/${eventId}`);
  }
};

// Opportunities services
export const opportunityService = {
  getOpportunities: async () => {
    return api.get('/opportunities/');
  },
  
  createOpportunity: async (opportunityData) => {
    return api.post('/opportunities/', opportunityData);
  },
  
  updateOpportunity: async (opportunityId, opportunityData) => {
    return api.put(`/opportunities/${opportunityId}`, opportunityData);
  },
  
  deleteOpportunity: async (opportunityId) => {
    return api.delete(`/opportunities/${opportunityId}`);
  },
  
  likeOpportunity: async (opportunityId) => {
    return api.post(`/opportunities/${opportunityId}/like`);
  },
  
  applyForOpportunity: async (opportunityId) => {
    return api.post(`/opportunities/${opportunityId}/apply`);
  }
};

export default {
  auth: authService,
  events: eventService,
  opportunities: opportunityService
}; 