let statsChart = null; // Global variable to store the chart instance

document.addEventListener('DOMContentLoaded', function() {
    const timeRangeSelect = document.getElementById('timeRange');
    timeRangeSelect.addEventListener('change', updateStats);
    updateStats();
});

function updateStats() {
    const timeRange = document.getElementById('timeRange').value;
    fetch(`/user_statistics?range=${timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.chart_data.datasets[0].data.length > 0) {
                document.getElementById('statsChart').style.display = 'block';
                document.getElementById('noDataMessage').style.display = 'none';
                createChart(data.chart_data);
                displayFunStats(data.fun_stats, data.time_range);
            } else {
                document.getElementById('statsChart').style.display = 'none';
                document.getElementById('noDataMessage').style.display = 'block';
            }
        });
}

function createChart(chartData) {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    // Destroy the existing chart if it exists
    if (statsChart) {
        statsChart.destroy();
    }
    
    statsChart = new Chart(ctx, {
        type: 'pie',
        data: chartData,
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Time Distribution'
            }
        }
    });
}

function displayFunStats(funStats, timeRange) {
    const funStatsDiv = document.getElementById('funStats');

    funStatsDiv.innerHTML = `
        <h3>Fun Facts</h3>
        <p>In the past ${timeRange}, you:</p>
        <ul>
            <li>- Studied for ${formatDuration(funStats.total_hours, 'hour')} [In Minutes: ${formatDuration(funStats.total_minutes, 'minute')}, In Seconds: ${formatDuration(funStats.total_seconds, 'second')}]</li>
            <li>- Completed ${funStats.work_sessions} work sessions [Total Sessions: ${funStats.work_sessions + funStats.short_breaks + funStats.long_breaks}]</li>
            <li>- Took ${funStats.short_breaks} short breaks and ${funStats.long_breaks} long breaks</li>
            <li>- Could have read ${funStats.books_read} books</li>
            <li>- Could have watched ${funStats.movies_watched} movies</li>
            <li>- Could have run ${funStats.marathons_run} marathons</li>
        </ul>
    `;
}

function formatDuration(value, unit) {
    if (value < 1000) {
        return value + ' ' + unit + (value === 1 ? '' : 's');
    } else if (value < 1000000) {
        return (value / 1000).toFixed(1) + 'K ' + unit + (value / 1000 === 1 ? '' : 's');
    } else {
        return (value / 1000000).toFixed(1) + 'M ' + unit + (value / 1000000 === 1 ? '' : 's');
    }
}