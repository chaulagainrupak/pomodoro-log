function toggleForm(form) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (form === 'login') {
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
    } else if (form === 'signup') {
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
    }
}
