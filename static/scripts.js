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

// Get the tab links and tab panes
const tabs = document.querySelectorAll('.tab-link');
const tabPanes = document.querySelectorAll('.tab-pane');

// Add event listener to each tab link
tabs.forEach((tab) => {
  tab.addEventListener('click', (e) => {
    // Get the target tab pane
    const targetTabPane = document.querySelector(`#${e.target.dataset.tab}`);

    // Remove active class from all tab panes
    tabPanes.forEach((tabPane) => {
      tabPane.classList.remove('active');
    });

    // Add active class to the target tab pane
    targetTabPane.classList.add('active');
  });
});

// Pomodoro timer function
let timerInterval = null;
let timerTime = 25 * 60; // 25 minutes

startButton.addEventListener('click', () => {
  startTimer();
});

resetButton.addEventListener('click', () => {
  resetTimer();
});

function startTimer() {
  timerInterval = setInterval(() => {
    timerTime--;
    updateTimerDisplay();
    if (timerTime <= 0) {
      resetTimer();
    }
  }, 1000);
}

function resetTimer() {
  clearInterval(timerInterval);
  timerTime = 25 * 60;
  updateTimerDisplay();
}

function updateTimerDisplay() {
  const minutes = Math.floor(timerTime / 60);
  const seconds = timerTime % 60;
  timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}