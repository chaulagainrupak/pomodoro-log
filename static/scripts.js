let currentTimerInterval;
let pomodoroDuration, shortBreakDuration, longBreakDuration;
let pomodoroCount = 0;

// Function to initialize the timer with durations
function initializeTimer() {
  const startButton = document.getElementById("startButton");
  if (startButton) {
      const onclickAttr = startButton.getAttribute("onclick");
      const match = onclickAttr.match(/startTimer\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (match) {
          pomodoroDuration = parseInt(match[1]);
          shortBreakDuration = parseInt(match[2]);
          longBreakDuration = parseInt(match[3]);
      }
  }
  
  // Set initial display
  updateTime(getCurrentMode());
  displayTimeLeft(pomodoroDuration * 60, 'pomodoroTime');
}

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
let startTimer = (pomoDuration, shortBreakDur, longBreakDur) => {
  pomodoroDuration = pomoDuration;
  shortBreakDuration = shortBreakDur;
  longBreakDuration = longBreakDur;

  if (currentTimerInterval) {
      clearInterval(currentTimerInterval);
  }

  const startButton = document.getElementById("startButton");
  if (!startButton) return;

  const currentMode = getCurrentMode();

  createCurrentSession();

  let duration;
  let timeDisplay;
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

  displayTimeLeft(duration * 60, timeDisplay);

  currentTimerInterval = setInterval(function() {
      const secondsLeft = Math.round((endTime - Date.now()) / 1000);

      if (secondsLeft < 0) {
          clearInterval(currentTimerInterval);
          playDingSound();
          switchToNextMode();
      } else {
          displayTimeLeft(secondsLeft, timeDisplay);
      }
  }, 1000);
};

// Function to switch to the next mode
function switchToNextMode() {
  const currentMode = getCurrentMode();
  
  let nextMode;

  if (currentMode === 'Pomodoro') {
    pomodoroCount++;
    if (pomodoroCount % 4 === 0) {
      nextMode = 'Long Break';
    } else {
      nextMode = 'Short Break';
    }
  } else {
    nextMode = 'Pomodoro';
  }

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

  const startButton = document.getElementById("resetButton") || document.getElementById("startButton");
  if (startButton) {
    startButton.innerText = "Start";
    startButton.setAttribute("id", "startButton");
    startButton.setAttribute("onclick", `startTimer(${pomodoroDuration}, ${shortBreakDuration}, ${longBreakDuration})`);
    startButton.style.backgroundColor = "";
  }
  
  updateTime(nextMode);
  startTimer(pomodoroDuration, shortBreakDuration, longBreakDuration);
}

// Function to reset the timer
let resetTimer = () => {
  if (currentTimerInterval) {
    clearInterval(currentTimerInterval);
    updateCurrentSession();
  }
  const resetButton = document.getElementById("resetButton");
  if (resetButton) {
    resetButton.innerText = "Start";
    resetButton.setAttribute("id", "startButton");
    resetButton.setAttribute("onclick", `startTimer(${pomodoroDuration}, ${shortBreakDuration}, ${longBreakDuration})`);
    resetButton.style.backgroundColor = "";
  }
  
  pomodoroCount = 0;  // Reset the Pomodoro count
  
  // Set the time display to the default value for the current mode
  const currentMode = getCurrentMode();
  let defaultDuration;
  let timeDisplay;
  switch (currentMode) {
    case 'Pomodoro':
      defaultDuration = pomodoroDuration;
      timeDisplay = 'pomodoroTime';
      break;
    case 'Short Break':
      defaultDuration = shortBreakDuration;
      timeDisplay = 'shortBreakTime';
      break;
    case 'Long Break':
      defaultDuration = longBreakDuration;
      timeDisplay = 'longBreakTime';
      break;
  }
  displayTimeLeft(defaultDuration * 60, timeDisplay);
};


// Function to display time left in timer
function displayTimeLeft(seconds, timeDisplayId) {
  const minutes = Math.floor(seconds / 60);
  const remainderSeconds = seconds % 60;
  const display = `${minutes}:${remainderSeconds < 10 ? '0' : ''}${remainderSeconds}`;
  document.getElementById(timeDisplayId).textContent = display;
  console.log(display);
}

// Function to play the ding sound
function playDingSound() {
  const dingSound = new Audio("/static/ding.mp3");
  dingSound.play();
}

// Function to update timer display based on selected mode
let updateTime = (mode) => {
  updateCurrentSession();


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
      modeDivs.forEach((d) => d.classList.remove("selected"));
      div.classList.add("selected");

      let mode = div.textContent.trim();
      updateTime(mode);

      if (currentTimerInterval) {
        clearInterval(currentTimerInterval);
      }

      pomodoroCount = 0;  // Reset the Pomodoro count when manually changing modes

      const startButton = document.getElementById("resetButton") || document.getElementById("startButton");
      if (startButton) {
        startButton.innerText = "Start";
        startButton.setAttribute("id", "startButton");
        startButton.setAttribute("onclick", `startTimer(${pomodoroDuration}, ${shortBreakDuration}, ${longBreakDuration})`);
        startButton.style.backgroundColor = "";
      }

      // Set the time display to the default value for the new mode
      let defaultDuration;
      let timeDisplay;
      switch (mode) {
        case 'Pomodoro':
          defaultDuration = pomodoroDuration;
          timeDisplay = 'pomodoroTime';
          break;
        case 'Short Break':
          defaultDuration = shortBreakDuration;
          timeDisplay = 'shortBreakTime';
          break;
        case 'Long Break':
          defaultDuration = longBreakDuration;
          timeDisplay = 'longBreakTime';
          break;
      }
      displayTimeLeft(defaultDuration * 60, timeDisplay);
    });
  });
};

let getCurrentMode = () => {
  let timerModes = document.querySelector(".timerModes");
  let selectedMode = timerModes.querySelector("div.selected");
  
  return selectedMode ? selectedMode.textContent.trim() : 'Pomodoro';
}

// Add event listener to DOMContentLoaded to initialize mode change functionality
document.addEventListener("DOMContentLoaded", function () {
  changeMode();
  initializeTimer();
});