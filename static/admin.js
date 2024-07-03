function activateUser(userId) {
    fetch(`/activate_user/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (response.ok) {
            alert('User activated successfully!');
            window.location.reload();
        } else {
            alert('Failed to activate user.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}


function filterTable() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.querySelector(".user-table");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, starting from the second row (index 1)
    for (i = 1; i < tr.length; i++) {
        var found = false;
        // Loop through all table cells in the current row
        for (j = 0; j < tr[i].cells.length - 1; j++) { // Exclude last cell (action buttons)
            td = tr[i].getElementsByTagName("td")[j];
            if (td) {
                txtValue = td.textContent || td.innerText;
                // Check if the current cell contains the search filter
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        // Set the display style based on whether the search filter was found
        tr[i].style.display = found ? "" : "none";
    }
}


function sortTable() {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.querySelector(".user-table");
    switching = true;

    // Get the index of the column to sort by
    var sortSelect = document.getElementById("sortSelect");
    var sortOption = sortSelect.options[sortSelect.selectedIndex].value;

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[getColumnIndex(sortOption)];
            y = rows[i + 1].getElementsByTagName("td")[getColumnIndex(sortOption)];

            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

function getColumnIndex(sortOption) {
    switch (sortOption) {
        case "username_asc":
        case "username_desc":
            return 0; // Username column index
        case "email_asc":
        case "email_desc":
            return 1; // Email column index
        case "signup_asc":
        case "signup_desc":
            return 2; // Signup Time column index
        default:
            return 0; // Default to Username column index
    }
}