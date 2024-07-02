
// Function to toggle between login and signup forms
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

let currentPhase = 'work';  // Initial phase is work session
let timerInterval;
const timeDisplay = document.getElementById('time');
const modeDisplay = document.getElementById('timer-mode');
const autoStartCheckbox = document.getElementById('autoStartCheckbox');

// Function to start the timer with given duration
function startTimer(pomodoroDuration, shortBreakDuration, longBreakDuration) {
    let duration;

    switch (currentPhase) {
        case 'work':
            duration = pomodoroDuration;
            modeDisplay.textContent = 'Pomodoro Mode';
            break;
        case 'short-break':
            duration = shortBreakDuration;
            modeDisplay.textContent = 'Short Break';
            break;
        case 'long-break':
            duration = longBreakDuration;
            modeDisplay.textContent = 'Long Break';
            break;
        default:
            duration = pomodoroDuration;
            modeDisplay.textContent = 'Pomodoro Mode';
    }

    duration *= 60;  // Convert to seconds
    const startButton = document.getElementById('startButton');
    startButton.innerText = 'Reset';
    startButton.setAttribute("id", "resetButton");
    startButton.setAttribute("onclick", "resetTimer()");
    startButton.style.backgroundColor = '#EE3940';

    const startTime = Date.now();
    const endTime = startTime + (duration * 1000);

    displayTimeLeft(duration);

    timerInterval = setInterval(function() {
        const secondsLeft = Math.round((endTime - Date.now()) / 1000);

        if (secondsLeft < 0) {
            clearInterval(timerInterval);
            dingSound.play();
            timeDisplay.textContent = 'Time is up!';

            // Switch to the next phase
            if (currentPhase === 'work') {
                currentPhase = 'short-break';
            } else if (currentPhase === 'short-break') {
                currentPhase = 'long-break';
            } else if (currentPhase === 'long-break') {
                currentPhase = 'work';
            }

            // Auto-start the next phase if the checkbox is checked
            if (autoStartCheckbox.checked) {
                startTimer(pomodoroDuration, shortBreakDuration, longBreakDuration);
            } else {
                // Update timer display for the next phase
                updateTimerDisplay(pomodoroDuration, shortBreakDuration, longBreakDuration);
            }
        } else {
            displayTimeLeft(secondsLeft);
        }
    }, 1000);
}

// Function to display time left in timer
function displayTimeLeft(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainderSeconds = seconds % 60;
    const display = `${minutes}:${remainderSeconds < 10 ? '0' : ''}${remainderSeconds}`;
    timeDisplay.textContent = display;
}

// Function to update timer display based on current phase
function updateTimerDisplay(pomodoroDuration, shortBreakDuration, longBreakDuration) {
    switch (currentPhase) {
        case 'work':
            timeDisplay.textContent = `${pomodoroDuration}:00`;
            modeDisplay.textContent = 'Pomodoro Mode';
            break;
        case 'short-break':
            timeDisplay.textContent = `${shortBreakDuration}:00`;
            modeDisplay.textContent = 'Short Break';
            break;
        case 'long-break':
            timeDisplay.textContent = `${longBreakDuration}:00`;
            modeDisplay.textContent = 'Long Break';
            break;
        default:
            timeDisplay.textContent = `${pomodoroDuration}:00`;
            modeDisplay.textContent = 'Pomodoro Mode';
    }
}

  // Function to reset the timer
  function resetTimer() {
      location.reload()
  }


