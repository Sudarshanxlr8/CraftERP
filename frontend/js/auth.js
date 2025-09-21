// Authentication and authorization functions

// Function to decode JWT token
function decodeJWT(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
}

// Function to protect pages based on user role
function protectPage(requiredRoles) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const decoded = decodeJWT(token);
        if (!decoded) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        
        const userRole = decoded.role.toLowerCase();
        const normalizedRequiredRoles = requiredRoles.map(role => role.toLowerCase());
        
        if (!normalizedRequiredRoles.some(role => role === userRole)) {
            alert('Access denied. Redirecting to dashboard.');
            window.location.href = '/index';
        }
    } catch (error) {
        console.error('Invalid token', error);
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
}

// Function to load navigation bar
function loadNavbar() {
    const navbarContainer = document.getElementById('navbar');
    if (!navbarContainer) return;
    
    const token = localStorage.getItem('token');
    let userRole = '';
    let username = '';
    
    if (token) {
        try {
            const decoded = decodeJWT(token);
            userRole = decoded.role.toLowerCase();
            username = decoded.username || decoded.sub || 'User';
        } catch (error) {
            console.error('Error decoding token for navbar:', error);
        }
    }
    
    let navbarHTML = `
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/index">Manufacturing System</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
    `;
    
    // Add menu items based on role
    if (userRole === 'administrator') {
        navbarHTML += `
            <li class="nav-item">
                <a class="nav-link" href="/users">Users</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/mo">Manufacturing Orders</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/bom">BOM</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/inventory">Inventory</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/reports">Reports</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/settings">Settings</a>
            </li>
        `;
    } else if (userRole === 'manufacturing manager') {
        navbarHTML += `
            <li class="nav-item">
                <a class="nav-link" href="/mo">Manufacturing Orders</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/wo">Work Orders</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/bom">BOM</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/reports">Reports</a>
            </li>
        `;
    } else if (userRole === 'inventory manager') {
        navbarHTML += `
            <li class="nav-item">
                <a class="nav-link" href="/inventory">Inventory</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/product-master">Products</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/reports">Reports</a>
            </li>
        `;
    } else if (userRole === 'operator') {
        navbarHTML += `
            <li class="nav-item">
                <a class="nav-link" href="/wo-task">My Tasks</a>
            </li>
        `;
    }
    
    // Add logout and profile section
    if (token) {
        navbarHTML += `
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <span class="navbar-text me-3">Welcome, ${username}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/profile">Profile</a>
                        </li>
                        <li class="nav-item">
                            <button class="btn btn-outline-light btn-sm" onclick="logout()">Logout</button>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        `;
    } else {
        navbarHTML += `
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="/login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/register">Register</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        `;
    }
    
    navbarContainer.innerHTML = navbarHTML;
}

// Function to handle logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login';
}

// Check if user is logged in
function isLoggedIn() {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
        const decoded = decodeJWT(token);
        return decoded !== null;
    } catch (error) {
        return false;
    }
}

// Get current user info
function getCurrentUser() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
        return decodeJWT(token);
    } catch (error) {
        return null;
    }
}