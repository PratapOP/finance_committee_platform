/**
 * API Client for Finance Committee Platform
 * Provides centralized API communication with error handling and authentication.
 */

// Configuration
const API_CONFIG = {
    BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://127.0.0.1:5000/api' 
        : '/api',
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000 // 1 second
};

/**
 * API Client Class
 * Handles all API communication with proper error handling and retry logic.
 */
class ApiClient {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Set authentication token
     */
    setAuthToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    /**
     * Clear authentication token
     */
    clearAuthToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    /**
     * Get default headers for API requests
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Handle API errors consistently
     */
    async handleApiError(response, data) {
        const error = {
            status: response.status,
            statusText: response.statusText,
            message: 'An error occurred',
            details: null
        };

        if (response.status === 401) {
            error.message = 'Authentication required. Please log in again.';
            this.clearAuthToken();
            // Redirect to login page or trigger login modal
            if (window.location.pathname !== '/') {
                window.location.href = '/';
            }
        } else if (response.status === 403) {
            error.message = 'Access denied. You don\'t have permission for this action.';
        } else if (response.status === 404) {
            error.message = 'The requested resource was not found.';
        } else if (response.status >= 500) {
            error.message = 'Server error. Please try again later.';
        } else if (data && data.error) {
            error.message = data.error;
            error.details = data.details || null;
        }

        return error;
    }

    /**
     * Retry failed requests with exponential backoff
     */
    async retryRequest(fn, attempts = API_CONFIG.RETRY_ATTEMPTS, delay = API_CONFIG.RETRY_DELAY) {
        try {
            return await fn();
        } catch (error) {
            if (attempts <= 1) {
                throw error;
            }

            // Don't retry on authentication errors
            if (error.status === 401 || error.status === 403) {
                throw error;
            }

            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, delay));
            
            // Exponential backoff
            return this.retryRequest(fn, attempts - 1, delay * 2);
        }
    }

    /**
     * Make HTTP request with timeout and error handling
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        config.signal = controller.signal;

        const makeRequest = async () => {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const error = await this.handleApiError(response, data);
                throw error;
            }

            return data;
        };

        return this.retryRequest(makeRequest);
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.makeRequest(endpoint, {
            method: 'GET'
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.makeRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.makeRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.makeRequest(endpoint, {
            method: 'DELETE'
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data) {
        return this.makeRequest(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    /**
     * Upload file with progress tracking
     */
    async upload(endpoint, file, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        const url = `${this.baseURL}${endpoint}`;

        return new Promise((resolve, reject) => {
            xhr.open('POST', url, true);
            
            // Set authentication header
            if (this.token) {
                xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
            }

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            xhr.onload = async () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        resolve(data);
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    let data;
                    try {
                        data = JSON.parse(xhr.responseText);
                    } catch (e) {
                        data = xhr.responseText;
                    }
                    const error = await this.handleApiError(
                        { status: xhr.status, statusText: xhr.statusText },
                        data
                    );
                    reject(error);
                }
            };

            xhr.onerror = () => {
                reject({
                    status: 0,
                    statusText: 'Network Error',
                    message: 'Network error. Please check your connection.'
                });
            };

            xhr.ontimeout = () => {
                reject({
                    status: 0,
                    statusText: 'Timeout',
                    message: 'Request timed out. Please try again.'
                });
            };

            xhr.timeout = this.timeout;
            xhr.send(formData);
        });
    }
}

// Create singleton instance
const api = new ApiClient();

/**
 * API Endpoints
 */
export const endpoints = {
    // Authentication
    AUTH: {
        LOGIN: '/auth/login',
        LOGOUT: '/auth/logout',
        REGISTER: '/auth/register',
        PROFILE: '/auth/profile',
        USERS: '/auth/users'
    },

    // Sponsors
    SPONSORS: '/sponsors',
    SPONSOR: (id) => `/sponsors/${id}`,

    // Events
    EVENTS: '/events',
    EVENT: (id) => `/events/${id}`,

    // Sponsorships
    SPONSORSHIPS: '/sponsorships',
    SPONSORSHIP: (id) => `/sponsorships/${id}`,

    // Analytics
    ANALYTICS: {
        OVERVIEW: '/analytics/overview',
        TRENDS: '/analytics/trends',
        ROI: '/analytics/roi',
        REPORTS: '/analytics/reports',
        DASHBOARD: '/analytics/dashboard'
    },

    // Settings
    SETTINGS: '/settings',

    // Sponsorships
    SPONSORSHIPS: '/sponsorships'
};

/**
 * API Methods
 */
export const apiMethods = {
    /**
     * Authentication methods
     */
    auth: {
        login: async (credentials) => {
            try {
                const result = await api.post(endpoints.AUTH.LOGIN, credentials);
                if (result.token) {
                    api.setAuthToken(result.token);
                }
                return result;
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },

        logout: async () => {
            try {
                await api.post(endpoints.AUTH.LOGOUT);
                api.clearAuthToken();
                return { success: true };
            } catch (error) {
                // Even if logout fails on server, clear local token
                api.clearAuthToken();
                console.error('Logout error:', error);
                throw error;
            }
        },

        register: async (userData) => {
            try {
                return await api.post(endpoints.AUTH.REGISTER, userData);
            } catch (error) {
                console.error('Registration failed:', error);
                throw error;
            }
        },

            getProfile: async () => {
                try {
                    return await api.get(endpoints.AUTH.PROFILE);
                } catch (error) {
                    console.error('Failed to get profile:', error);
                    throw error;
                }
            },

            deleteUser: async (userId) => {
                try {
                    return await api.delete(`${endpoints.AUTH.USERS}/${userId}`);
                } catch (error) {
                    console.error('Failed to delete user:', error);
                    throw error;
                }
            }
    },

    /**
     * Sponsor methods
     */
    sponsors: {
        getAll: async () => {
            try {
                return await api.get(endpoints.SPONSORS);
            } catch (error) {
                console.error('Failed to fetch sponsors:', error);
                throw error;
            }
        },

        getById: async (id) => {
            try {
                return await api.get(endpoints.SPONSOR(id));
            } catch (error) {
                console.error(`Failed to fetch sponsor ${id}:`, error);
                throw error;
            }
        },

        create: async (sponsorData) => {
            try {
                return await api.post(endpoints.SPONSORS, sponsorData);
            } catch (error) {
                console.error('Failed to create sponsor:', error);
                throw error;
            }
        },

        update: async (id, sponsorData) => {
            try {
                return await api.put(endpoints.SPONSOR(id), sponsorData);
            } catch (error) {
                console.error(`Failed to update sponsor ${id}:`, error);
                throw error;
            }
        },

        delete: async (id) => {
            try {
                return await api.delete(endpoints.SPONSOR(id));
            } catch (error) {
                console.error(`Failed to delete sponsor ${id}:`, error);
                throw error;
            }
        }
    },

    /**
     * Event methods
     */
    events: {
        getAll: async () => {
            try {
                return await api.get(endpoints.EVENTS);
            } catch (error) {
                console.error('Failed to fetch events:', error);
                throw error;
            }
        },

        getById: async (id) => {
            try {
                return await api.get(endpoints.EVENT(id));
            } catch (error) {
                console.error(`Failed to fetch event ${id}:`, error);
                throw error;
            }
        },

        create: async (eventData) => {
            try {
                return await api.post(endpoints.EVENTS, eventData);
            } catch (error) {
                console.error('Failed to create event:', error);
                throw error;
            }
        },

        update: async (id, eventData) => {
            try {
                return await api.put(endpoints.EVENT(id), eventData);
            } catch (error) {
                console.error(`Failed to update event ${id}:`, error);
                throw error;
            }
        },

        delete: async (id) => {
            try {
                return await api.delete(endpoints.EVENT(id));
            } catch (error) {
                console.error(`Failed to delete event ${id}:`, error);
                throw error;
            }
        }
    },

    /**
     * Analytics methods
     */
    analytics: {
        getOverview: async () => {
            try {
                return await api.get(endpoints.ANALYTICS.OVERVIEW);
            } catch (error) {
                console.error('Failed to fetch analytics overview:', error);
                throw error;
            }
        },

        getTrends: async (params = {}) => {
            try {
                const queryString = new URLSearchParams(params).toString();
                const url = queryString 
                    ? `${endpoints.ANALYTICS.TRENDS}?${queryString}`
                    : endpoints.ANALYTICS.TRENDS;
                return await api.get(url);
            } catch (error) {
                console.error('Failed to fetch trends:', error);
                throw error;
            }
        },

        getROI: async (params = {}) => {
            try {
                const queryString = new URLSearchParams(params).toString();
                const url = queryString 
                    ? `${endpoints.ANALYTICS.ROI}?${queryString}`
                    : endpoints.ANALYTICS.ROI;
                return await api.get(url);
            } catch (error) {
                console.error('Failed to fetch ROI data:', error);
                throw error;
            }
        },

        getReports: async (params = {}) => {
            try {
                const queryString = new URLSearchParams(params).toString();
                const url = queryString 
                    ? `${endpoints.ANALYTICS.REPORTS}?${queryString}`
                    : endpoints.ANALYTICS.REPORTS;
                return await api.get(url);
            } catch (error) {
                console.error('Failed to fetch reports:', error);
                throw error;
            }
        },

        getDashboard: async () => {
            try {
                return await api.get(endpoints.ANALYTICS.DASHBOARD);
            } catch (error) {
                console.error('Failed to fetch dashboard analytics:', error);
                throw error;
            }
        }
    },

    /**
     * Admin methods
     */
    admin: {
        saveSettings: async (settings) => {
            try {
                return await api.put(endpoints.SETTINGS, settings);
            } catch (error) {
                console.error('Failed to save settings:', error);
                throw error;
            }
        },

        getSettings: async () => {
            try {
                return await api.get(endpoints.SETTINGS);
            } catch (error) {
                console.error('Failed to get settings:', error);
                throw error;
            }
        },

        getSystemInfo: async () => {
            try {
                return await api.get(`${endpoints.SETTINGS}/system-info`);
            } catch (error) {
                console.error('Failed to get system info:', error);
                throw error;
            }
        }
    },

    /**
     * Sponsorship methods
     */
    sponsorships: {
        getAll: async (params = {}) => {
            try {
                const queryString = new URLSearchParams(params).toString();
                const url = queryString 
                    ? `${endpoints.SPONSORSHIPS}?${queryString}`
                    : endpoints.SPONSORSHIPS;
                return await api.get(url);
            } catch (error) {
                console.error('Failed to fetch sponsorships:', error);
                throw error;
            }
        },

        getById: async (id) => {
            try {
                return await api.get(`${endpoints.SPONSORSHIPS}/${id}`);
            } catch (error) {
                console.error(`Failed to fetch sponsorship ${id}:`, error);
                throw error;
            }
        },

        create: async (sponsorshipData) => {
            try {
                return await api.post(endpoints.SPONSORSHIPS, sponsorshipData);
            } catch (error) {
                console.error('Failed to create sponsorship:', error);
                throw error;
            }
        },

        update: async (id, sponsorshipData) => {
            try {
                return await api.put(`${endpoints.SPONSORSHIPS}/${id}`, sponsorshipData);
            } catch (error) {
                console.error(`Failed to update sponsorship ${id}:`, error);
                throw error;
            }
        },

        delete: async (id) => {
            try {
                return await api.delete(`${endpoints.SPONSORSHIPS}/${id}`);
            } catch (error) {
                console.error(`Failed to delete sponsorship ${id}:`, error);
                throw error;
            }
        },

        getStats: async () => {
            try {
                return await api.get(`${endpoints.SPONSORSHIPS}/stats`);
            } catch (error) {
                console.error('Failed to fetch sponsorship stats:', error);
                throw error;
            }
        },

        getBySponsor: async (sponsorId) => {
            try {
                return await api.get(`${endpoints.SPONSORSHIPS}/by-sponsor/${sponsorId}`);
            } catch (error) {
                console.error(`Failed to fetch sponsor sponsorships ${sponsorId}:`, error);
                throw error;
            }
        },

        getByEvent: async (eventId) => {
            try {
                return await api.get(`${endpoints.SPONSORSHIPS}/by-event/${eventId}`);
            } catch (error) {
                console.error(`Failed to fetch event sponsorships ${eventId}:`, error);
                throw error;
            }
        }
    }
};

/**
 * Utility functions
 */
export const apiUtils = {
    /**
     * Show error message to user
     */
    showError: (error, containerId = 'error-container') => {
        const errorContainer = document.getElementById(containerId);
        if (errorContainer) {
            errorContainer.textContent = error.message || 'An error occurred';
            errorContainer.style.display = 'block';
            errorContainer.className = 'error-message show';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorContainer.style.display = 'none';
                errorContainer.className = 'error-message';
            }, 5000);
        }
    },

    /**
     * Show success message to user
     */
    showSuccess: (message, containerId = 'success-container') => {
        const successContainer = document.getElementById(containerId);
        if (successContainer) {
            successContainer.textContent = message;
            successContainer.style.display = 'block';
            successContainer.className = 'success-message show';
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                successContainer.style.display = 'none';
                successContainer.className = 'success-message';
            }, 3000);
        }
    },

    /**
     * Show loading state
     */
    setLoading: (loading, containerId = 'loading-spinner') => {
        const loader = document.getElementById(containerId);
        if (loader) {
            loader.style.display = loading ? 'block' : 'none';
        }
    },

    /**
     * Format currency for display
     */
    formatCurrency: (amount, currency = '₹') => {
        return `${currency} ${Number(amount).toLocaleString('en-IN')}`;
    },

    /**
     * Format date for display
     */
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Debounce function to prevent rapid API calls
     */
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

export default api;