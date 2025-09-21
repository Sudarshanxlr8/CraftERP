// Utility functions for the application

// Function to show loading spinner
function showLoading(elementId = 'loading') {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
}

// Function to hide loading spinner
function hideLoading(elementId = 'loading') {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// Function to show error message
function showError(message, elementId = 'error-message') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        errorElement.className = 'alert alert-danger';
    } else {
        alert('Error: ' + message);
    }
}

// Function to hide error message
function hideError(elementId = 'error-message') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// Function to show success message
function showSuccess(message, elementId = 'success-message') {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
        successElement.className = 'alert alert-success';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            hideSuccess(elementId);
        }, 3000);
    } else {
        alert('Success: ' + message);
    }
}

// Function to hide success message
function hideSuccess(elementId = 'success-message') {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.style.display = 'none';
    }
}

// Function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Function to validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to validate password
function validatePassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
}

// Function to sanitize input
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

// Function to handle API errors
function handleApiError(response, defaultMessage = 'An error occurred') {
    if (!response.ok) {
        if (response.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('token');
            window.location.href = '/login';
            return 'Session expired. Please login again.';
        } else if (response.status === 403) {
            return 'Access denied. You do not have permission to perform this action.';
        } else if (response.status === 404) {
            return 'Resource not found.';
        } else if (response.status >= 500) {
            return 'Server error. Please try again later.';
        } else {
            return defaultMessage;
        }
    }
    return null;
}

// Function to debounce
function debounce(func, wait) {
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

// Function to throttle
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess('Copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy to clipboard');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccess('Copied to clipboard!');
    }
}

// Function to generate random ID
function generateId(prefix = 'id') {
    return prefix + '_' + Math.random().toString(36).substr(2, 9);
}

// Function to check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Function to animate number counting
function animateNumber(element, start, end, duration = 1000) {
    const startTime = performance.now();
    const difference = end - start;
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + difference * progress);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showLoading,
        hideLoading,
        showError,
        hideError,
        showSuccess,
        hideSuccess,
        formatDate,
        formatCurrency,
        validateEmail,
        validatePassword,
        sanitizeInput,
        handleApiError,
        debounce,
        throttle,
        copyToClipboard,
        generateId,
        isInViewport,
        animateNumber
    };
}