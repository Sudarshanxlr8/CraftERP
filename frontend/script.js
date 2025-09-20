function displayUsername() {
    const token = localStorage.getItem('token');
    if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        document.getElementById('username').textContent = payload.username || 'User';
    } else {
        window.location.href = 'login.html';
    }
}

// Register form handling
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData);
        try {
            const response = await fetch('/register', {  // Changed to relative URL
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Registered successfully');
                window.location.href = '/index';  // Changed to relative URL
            } else {
                alert(result.error);
            }
        } catch (err) {
            alert('Error registering');
        }
    });
}

// Login form handling
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData);
        try {
            const response = await fetch('/login', {  // Changed to relative URL
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                localStorage.setItem('token', result.token);
                window.location.href = '/index';  // Changed to relative URL
            } else {
                alert(result.error);
            }
        } catch (err) {
            alert('Error logging in');
        }
    });
}