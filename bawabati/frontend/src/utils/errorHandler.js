/**
 * Standardized API error handling utility
 * Use this to handle errors consistently across the app
 */

export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with an error status code
    const status = error.response.status;
    const message = error.response.data?.message || 
                    error.response.data?.detail || 
                    'An error occurred';
    
    // Map specific status codes to user-friendly messages
    switch (status) {
      case 400:
        return { 
          success: false,
          status,
          message: message || 'Invalid request. Please check your data.'
        };
      case 401:
        return { 
          success: false,
          status,
          message: 'Authentication required. Please log in.'
        };
      case 403:
        return { 
          success: false,
          status,
          message: 'You do not have permission to perform this action.'
        };
      case 404:
        return { 
          success: false,
          status, 
          message: 'The requested resource was not found.'
        };
      case 500:
        return { 
          success: false,
          status,
          message: 'Server error. Please try again later.'
        };
      default:
        return { 
          success: false,
          status,
          message
        };
    }
  } else if (error.request) {
    // Request was made but no response received (network error)
    return { 
      success: false,
      message: 'No response from server. Please check your connection.'
    };
  } else {
    // Something else happened while setting up the request
    return { 
      success: false,
      message: error.message || 'An unexpected error occurred.'
    };
  }
};

/**
 * Async function wrapper with built-in error handling
 * Use this to wrap async API calls in components
 * 
 * @example
 * const fetchData = async () => {
 *   const { data, error } = await withErrorHandling(
 *     () => api.get('/data/')
 *   );
 *   
 *   if (error) {
 *     setError(error.message);
 *     return;
 *   }
 *   
 *   setData(data);
 * };
 */
export const withErrorHandling = async (asyncFn) => {
  try {
    const response = await asyncFn();
    return { data: response.data, error: null };
  } catch (error) {
    const handledError = handleApiError(error);
    return { data: null, error: handledError };
  }
};

export default { handleApiError, withErrorHandling }; 