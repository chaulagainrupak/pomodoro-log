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


