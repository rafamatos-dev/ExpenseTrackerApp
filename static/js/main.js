// static/js/main.js - Main JavaScript file

// Function to check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('userId') !== null;
}

// Function to update nav based on login state
function updateNavigation() {
    const loginBtn = document.getElementById('login-btn');
    const addExpenseBtn = document.getElementById('add-expense-btn');
    
    if (isLoggedIn()) {
        // User is logged in
        if (loginBtn) {
            loginBtn.textContent = 'Logout';
            loginBtn.href = '#';
            loginBtn.addEventListener('click', function(e) {
                e.preventDefault();
                logout();
            });
        }
        
        // Enable Add Expense functionality
        if (addExpenseBtn) {
            addExpenseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                // Redirect to expense form or show modal
                window.location.href = '/expenses/new';
            });
        }
    } else {
        // User is not logged in
        if (loginBtn) {
            loginBtn.textContent = 'Login';
            loginBtn.href = '/login';
        }
        
        // Disable Add Expense functionality
        if (addExpenseBtn) {
            addExpenseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('Please log in to add expenses');
                window.location.href = '/login';
            });
        }
    }
}

// Function to log out
function logout() {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    // Redirect to home page
    window.location.href = '/';
}

// Handle login form submission
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/users/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Store user info in localStorage
                    localStorage.setItem('userId', data.user._id);
                    localStorage.setItem('username', data.user.username);
                    
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    // Show error message
                    const errorElement = document.getElementById('login-error');
                    if (errorElement) {
                        errorElement.textContent = data.error || 'Login failed';
                        errorElement.style.display = 'block';
                    }
                }
            } catch (error) {
                console.error('Login error:', error);
            }
        });
    }
}

// Handle registration form submission
function setupRegisterForm() {
    const registerForm = document.getElementById('register-form');
    
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/users/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Show success message
                    alert('Registration successful! Please log in.');
                    
                    // Redirect to login page
                    window.location.href = '/login';
                } else {
                    // Show error messages
                    const errorsContainer = document.getElementById('register-errors');
                    if (errorsContainer) {
                        errorsContainer.innerHTML = '';
                        
                        if (typeof data.errors === 'object') {
                            for (const field in data.errors) {
                                const errorElement = document.createElement('div');
                                errorElement.className = 'alert alert-danger';
                                errorElement.textContent = data.errors[field];
                                errorsContainer.appendChild(errorElement);
                            }
                        } else {
                            const errorElement = document.createElement('div');
                            errorElement.className = 'alert alert-danger';
                            errorElement.textContent = data.error || 'Registration failed';
                            errorsContainer.appendChild(errorElement);
                        }
                    }
                }
            } catch (error) {
                console.error('Registration error:', error);
            }
        });
    }
}

// Check for protected pages
function checkProtectedPage() {
    // List of pages that require authentication
    const protectedPages = ['/dashboard', '/expenses/new', '/expenses/edit', '/categories'];
    
    // Check if current page is protected
    const isProtectedPage = protectedPages.some(page => window.location.pathname.startsWith(page));
    
    if (isProtectedPage && !isLoggedIn()) {
        // Redirect to login page
        alert('Please log in to access this page');
        window.location.href = '/login';
        return false;
    }
    
    return true;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Update navigation based on login state
    updateNavigation();
    
    // Setup forms if they exist
    setupLoginForm();
    setupRegisterForm();
    
    // Check if this is a protected page
    checkProtectedPage();
});