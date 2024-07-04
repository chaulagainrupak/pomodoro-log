let pieChart = null; // Global variable to store the pie chart instance
let lineChart = null; // Global variable to store the line chart instance

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
            if (data.pie_chart_data.datasets[0].data.length > 0) {
                document.getElementById('pieChart').style.display = 'block';
                document.getElementById('noPieDataMessage').style.display = 'none';
                createPieChart(data.pie_chart_data);
                createLineChart(data.line_chart_data, timeRange);
                displayFunStats(data.fun_stats, data.time_range);
            } else {
                document.getElementById('pieChart').style.display = 'none';
                document.getElementById('noPieDataMessage').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('pieChart').style.display = 'none';
            document.getElementById('noPieDataMessage').style.display = 'block';
        });
}

function createPieChart(chartData) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    
    // Destroy the existing chart if it exists
    if (pieChart) {
        pieChart.destroy();
    }
    
    pieChart = new Chart(ctx, {
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

function createLineChart(chartData, timeRange) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    
    // Destroy the existing chart if it exists
    if (lineChart) {
        lineChart.destroy();
    }

    // Prepare data for line chart
    const formattedData = {
        labels: chartData.labels,
        datasets: [{
            label: 'Session Durations (hours)',
            data: chartData.datasets[0].data.map(duration => duration / 3600), // Convert seconds to hours
            fill: false,
            borderColor: 'rgba(75, 192, 192, 1)',
            lineTension: 0.1
        }]
    };

    lineChart = new Chart(ctx, {
        type: 'line',
        data: formattedData,
        options: {
            responsive: true,
            title: {
                display: true,
                text: `Session Durations for ${timeRange}`
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value, index, values) {
                            return value + 'h';
                        }
                    }
                }]
            }
        }
    });
}

function displayFunStats(funStats, timeRange) {
    const funStatsDiv = document.getElementById('funStats');

    if (timeRange == 'all_time'){
        timeRange = 'All Time';
    }
    funStatsDiv.innerHTML = `
        <h3>Fun Facts</h3>
        <p>In the past ${timeRange}, you:</p>
        <ul>
            <li>- Studied for ${formatDuration(funStats.total_hours, 'hour')}</li>
            <li>- Completed ${funStats.work_sessions} work sessions</li>
            <li>- Took ${funStats.short_breaks} short breaks and ${funStats.long_breaks} long breaks</li>
            <li>- Could have read ${funStats.books_read} books</li>
            <li>- Could have watched ${funStats.movies_watched} movies</li>
            <li>- Could have run ${funStats.marathons_run} marathons</li>
            <li>- Could have read ${funStats.articles_read} articles</li>
            <li>- Could have written ${funStats.blog_posts_written} blog posts</li>
            <li>- Could have listened to ${funStats.songs_listened} songs</li>
            <li>- Could have listened to ${funStats.podcasts_listened} podcasts</li>
            <li>- Could have taken ${funStats.naps_taken} naps</li>
        </ul>
    `;
}

function formatDuration(value, unit) {
    if (value < 1000) {
        return value.toFixed(2) + ' ' + unit + (value === 1 ? '' : 's');
    } else if (value < 1000000) {
        return (value / 1000).toFixed(2) + 'K ' + unit + (value / 1000 === 1 ? '' : 's');
    } else {
        return (value / 1000000).toFixed(2) + 'M ' + unit + (value / 1000000 === 1 ? '' : 's');
    }
}
