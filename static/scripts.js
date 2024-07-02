let currentTimerInterval;
// Function to toggle between login and signup forms
function toggleForm(form) {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");

  if (form === "login") {
    loginForm.classList.add("active");
    signupForm.classList.remove("active");
  } else if (form === "signup") {
    loginForm.classList.remove("active");
    signupForm.classList.add("active");
  }
}

// Function to start the timer with given duration in minutes
let startTimer = (pomodoroDuration, shortBreakDuration, longBreakDuration) => {
  if (currentTimerInterval) {
    clearInterval(currentTimerInterval);
  }

  const startButton = document.getElementById("startButton");
  if (!startButton) return;

  const currentMode = getCurrentMode();
  let duration;
  switch (currentMode) {
    case 'Pomodoro':
      duration = pomodoroDuration;
      timeDisplay = 'pomodoroTime';
      break;
    case 'Short Break':
      duration = shortBreakDuration;
      timeDisplay = 'shortBreakTime';
      break;
    case 'Long Break':
      duration = longBreakDuration;
      timeDisplay = 'longBreakTime';
      break;
  }

  console.log(duration);
  startButton.innerText = "Reset";
  startButton.setAttribute("id", "resetButton");
  startButton.setAttribute("onclick", "resetTimer()");
  startButton.style.backgroundColor = "#EE3940";

  updateTime(currentMode);

  const endTime = Date.now() + (duration * 60 * 1000);

  displayTimeLeft(duration * 60);

  currentTimerInterval = setInterval(function() {
    const secondsLeft = Math.round((endTime - Date.now()) / 1000);

    if (secondsLeft < 0) {
      clearInterval(currentTimerInterval);
      playDingSound();
      document.getElementById(timeDisplay).textContent = 'Time is up!';
      startNextMode(pomodoroDuration, shortBreakDuration, longBreakDuration);
    } else {
      displayTimeLeft(secondsLeft);
    }
  }, 1000);
};

// Function to reset the timer
let resetTimer = () => {
  if (currentTimerInterval) {
    clearInterval(currentTimerInterval);
  }
  const startButton = document.getElementById("resetButton");
  startButton.innerText = "Start";
  startButton.setAttribute("id", "startButton");
  startButton.setAttribute("onclick", 'startTimer({{ preferences.pomodoro_duration }}, {{ preferences.short_break_duration }}, {{ preferences.long_break_duration }})');
  startButton.style.backgroundColor = "";
  displayTimeLeft(0);
};

// Function to display time left in timer
function displayTimeLeft(seconds) {
  switch (getCurrentMode) {
    case 'Pomodoro':
      timeDisplay = 'pomodoroTime';
      break;
    case 'Short Break':
      timeDisplay = 'shortBreakTime';
      break;
    case 'Long Break':
      timeDisplay = 'longBreakTime';
      break;
  }
  const minutes = Math.floor(seconds / 60);
  const remainderSeconds = seconds % 60;
  const display = `${minutes}:${remainderSeconds < 10 ? '0' : ''}${remainderSeconds}`;
  document.getElementById(timeDisplay).textContent = display;
  console.log(display);
}

// Function to play the ding sound
function playDingSound() {
  // Adjust or comment out if you don't have a sound file
  const dingSound = new Audio("/static/ding.mp3"); // Replace with your audio file
  dingSound.play();
}

// Function to update timer display based on selected mode
let updateTime = (mode) => {
  switch (mode) {
    case "Pomodoro":
      document.getElementById('pomodoroTime').classList.remove('hidden');
      document.getElementById('shortBreakTime').classList.add('hidden');
      document.getElementById('longBreakTime').classList.add('hidden');
      break;
    case "Short Break":
      document.getElementById('pomodoroTime').classList.add('hidden');
      document.getElementById('shortBreakTime').classList.remove('hidden');
      document.getElementById('longBreakTime').classList.add('hidden');
      break;
    case "Long Break":
      document.getElementById('pomodoroTime').classList.add('hidden');
      document.getElementById('shortBreakTime').classList.add('hidden');
      document.getElementById('longBreakTime').classList.remove('hidden');
      break;
    default:
      break;
  }
};

// Initialize timer mode change functionality
let changeMode = () => {
  let timerModes = document.querySelector(".timerModes");
  let modeDivs = timerModes.querySelectorAll("div");

  modeDivs.forEach((div) => {
    div.addEventListener("click", () => {
      modeDivs.forEach((d) => {
        d.classList.remove("selected");
      });

      div.classList.add("selected");

      let mode = div.textContent.trim();
      updateTime(mode);

      // Stop the current timer
      if (currentTimerInterval) {
        clearInterval(currentTimerInterval);
      }

      // Reset the start button
      const startButton = document.getElementById("resetButton") || document.getElementById("startButton");
      startButton.innerText = "Start";
      startButton.setAttribute("id", "startButton");
      startButton.setAttribute("onclick", 'startTimer({{ preferences.pomodoro_duration }}, {{ preferences.short_break_duration }}, {{ preferences.long_break_duration }})');
      startButton.style.backgroundColor = "";

      // Reset the timer display
      displayTimeLeft(0);
    });
  });
};

let getCurrentMode = () => {
  let timerModes = document.querySelector(".timerModes");
  let selectedMode = timerModes.querySelector("div.selected");
  
  if (selectedMode) {
    return selectedMode.textContent.trim();
  } else {
    // Default to 'Pomodoro' if no mode is selected
    return 'Pomodoro';
  }
}

function startNextMode(pomodoroDuration, shortBreakDuration, longBreakDuration) {
  const modes = ['Pomodoro', 'Short Break', 'Long Break'];
  const currentMode = getCurrentMode();
  const currentIndex = modes.indexOf(currentMode);
  const nextIndex = (currentIndex + 1) % modes.length;
  const nextMode = modes[nextIndex];

  // Update the selected mode visually
  let timerModes = document.querySelector(".timerModes");
  let modeDivs = timerModes.querySelectorAll("div");
  modeDivs.forEach((div) => {
    if (div.textContent.trim() === nextMode) {
      div.classList.add("selected");
    } else {
      div.classList.remove("selected");
    }
  });

  updateTime(nextMode);
  startTimer(pomodoroDuration, shortBreakDuration, longBreakDuration);
}
// Add event listener to DOMContentLoaded to initialize mode change functionality
document.addEventListener("DOMContentLoaded", function () {
  changeMode(); // Initialize mode change functionality
});
