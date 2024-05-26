// Serversteuerungsfunktionen
function controlServer(action) {
    fetch(`/server/${action}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('serverMessage').textContent = data.message;
    });
}

// Daten für Graphen
let cpuData = [];
let ramData = [];
let labels = [];

function fetchSystemInfo() {
    fetch('/system_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpuUsage').textContent = data.cpu_usage;
            document.getElementById('ramUsage').textContent = data.ram_usage;
            document.getElementById('uptime').textContent = data.uptime;

            // Update data arrays
            if (cpuData.length >= 10) {
                cpuData.shift();
                ramData.shift();
                labels.shift();
            }
            cpuData.push(data.cpu_usage);
            ramData.push(data.ram_usage);
            labels.push(new Date().toLocaleTimeString());

            // Update charts
            cpuChart.update();
            ramChart.update();
        });
}

// Chart.js initialisieren
const ctxCpu = document.getElementById('cpuChart').getContext('2d');
const ctxRam = document.getElementById('ramChart').getContext('2d');

const cpuChart = new Chart(ctxCpu, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'CPU Usage (%)',
            data: cpuData,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'second'
                }
            },
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

const ramChart = new Chart(ctxRam, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'RAM Usage (%)',
            data: ramData,
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'second'
                }
            },
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

setInterval(fetchSystemInfo, 5000);
fetchSystemInfo();
