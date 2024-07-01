
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
  function startTimer(duration) {
    duration  = duration * 60;
    shortBreakDuration = 1;
    longBreakDuration = 2;
    document.getElementById('startButton').style.display = 'none';
    document.getElementById('resetButton').style.display = 'block';
    
      const startTime = Date.now();
      const endTime = startTime + (duration * 1000);

      displayTimeLeft(duration);

      timerInterval = setInterval(function() {
          const secondsLeft = Math.round((endTime - Date.now()) / 1000);

          if (secondsLeft < 0) {
              clearInterval(timerInterval);
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
                  switch (currentPhase) {
                      case 'work':
                          startTimer(pomodoroDuration);
                          modeDisplay.textContent = 'Pomodoro Mode';
                          break;
                      case 'short-break':
                          startTimer(shortBreakDuration);
                          modeDisplay.textContent = 'Short Break';
                          break;
                      case 'long-break':
                          startTimer(longBreakDuration);
                          modeDisplay.textContent = 'Long Break';
                          break;
                      default:
                          break;
                  }
              } else {
                  // Update timer display for the next phase
                  updateTimerDisplay();
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
  function updateTimerDisplay() {
      switch (currentPhase) {
          case 'work':
              timeDisplay.textContent = `${pomodoroDuration / 60}:00`;
              modeDisplay.textContent = 'Pomodoro Mode';
              break;
          case 'short-break':
              timeDisplay.textContent = `${shortBreakDuration / 60}:00`;
              modeDisplay.textContent = 'Short Break';
              break;
          case 'long-break':
              timeDisplay.textContent = `${longBreakDuration / 60}:00`;
              modeDisplay.textContent = 'Long Break';
              break;
          default:
              break;
      }
  }

  // Function to reset the timer
  function resetTimer() {
      location.reload()
  }


