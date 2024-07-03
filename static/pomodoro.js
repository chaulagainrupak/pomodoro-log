let createCurrentSession = () => {
    let phase = getCurrentMode();
    let sessionData = {
        start_time: Math.floor(new Date().getTime() / 1000), // Convert current time to epoch time in seconds
        phase: phase
    };

    fetch('/createSession', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sessionData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => { throw new Error(error.error); });
        }
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


let updateCurrentSession = () => {
    let phase = getCurrentMode();
    let sessionData = {
        end_time: Math.floor(new Date().getTime() / 1000), // Convert current time to epoch time in seconds
        phase: phase
    };

    fetch('/updateSession', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sessionData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => { throw new Error(error.error); });
        }
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function updateClockMask(seconds, totalSeconds) {
    const progress = seconds / totalSeconds;
    const degrees = progress * 360;
    const clockMask = document.querySelector('.clock-mask');
    
    if (degrees <= 180) {
        clockMask.style.transform = `rotate(${degrees}deg)`;
    } else {
        clockMask.style.transform = `rotate(180deg)`;
        clockMask.style.width = '100%';
        clockMask.style.transform = `rotate(${degrees}deg)`;
    }
}

function resetClock() {
    const clockMask = document.querySelector('.clock-mask');
    clockMask.style.transform = 'rotate(0deg)';
    clockMask.style.width = '50%';
}

function initializeClock() {
    const clockFace = document.querySelector('.clock-face');
    if (!clockFace.querySelector('.clock-mask')) {
        const clockMask = document.createElement('div');
        clockMask.className = 'clock-mask';
        clockFace.appendChild(clockMask);
    }
}

function resetClock() {
    document.querySelector('.clock-mask').style.transform = 'rotate(0deg)';
}

