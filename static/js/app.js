document.addEventListener('DOMContentLoaded', () => {
    // Configuration for each sensor's chart
    const sensorConfigs = {
        'temperature': {
            endpoint: '/data/temperature',
            chartId: 'temperatureChart',
            label: 'Temperature (°C)',
            color: 'rgba(255, 99, 132, 1)', // Red
            cardValueId: 'temp-value',
            cardTimeId: 'temp-time'
        },
        'humidity': {
            endpoint: '/data/humidity',
            chartId: 'humidityChart',
            label: 'Humidity (%)',
            color: 'rgba(54, 162, 235, 1)', // Blue
            cardValueId: 'humidity-value',
            cardTimeId: 'humidity-time'
        },
        'light': {
            endpoint: '/data/light',
            chartId: 'lightChart',
            label: 'Light (lux)',
            color: 'rgba(255, 206, 86, 1)', // Yellow
            cardValueId: 'light-value',
            cardTimeId: 'light-time'
        }
    };

    const charts = {}; // To store Chart.js instances

    // Declarations for DOM elements
    const body = document.body;
    const toggleButton = document.getElementById('theme-toggle');
    const lightIcon = document.querySelector('.light-icon');
    const darkIcon = document.querySelector('.dark-icon');

    function toggleTheme() {
        body.classList.toggle('dark-theme');
        const isDark = body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Update button text
        lightIcon.style.display = isDark ? 'none' : 'inline';
        darkIcon.style.display = isDark ? 'inline' : 'none';

        // Re-render all charts to apply new color settings
        // This line is safe because 'charts' is declared above
        Object.values(charts).forEach(chart => {
            const chartType = chart.canvas.id.replace('Chart', '');
            updateChartAppearance(chart, chartType);
            chart.update();
        });
    }

    /**
     * Updates the chart and the last reading card for a specific sensor.
     */
    async function updateSensorData(sensorType) {
        const config = sensorConfigs[sensorType];

        try {
            const response = await fetch(config.endpoint);
            const data = await response.json();

            // The data is ordered DESC by timestamp, so the first element is the latest
            const latestReading = data[0];

            // 1. Update the 'Real-time' card
            if (latestReading) {
                document.getElementById(config.cardValueId).textContent = latestReading.value.toFixed(2);
                document.getElementById(config.cardTimeId).textContent = 'Last updated: ' + new Date(latestReading.timestamp).toLocaleTimeString();
            }

            // Reverse the data so it's chronologically ordered for the chart
            data.reverse();

            // Extract timestamps for X-axis (labels) and values for Y-axis
            const timestamps = data.map(item => new Date(item.timestamp).toLocaleTimeString());
            const values = data.map(item => item.value);

            // 2. Update the Chart
            if (charts[sensorType]) {
                // Update existing chart
                charts[sensorType].data.labels = timestamps;
                charts[sensorType].data.datasets[0].data = values;
                charts[sensorType].update();
            } else {
                // Initialize the chart
                const ctx = document.getElementById(config.chartId).getContext('2d');
                charts[sensorType] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: timestamps,
                        datasets: [{
                            label: config.label,
                            data: values,
                            borderColor: config.color,
                            backgroundColor: config.color.replace('1)', '0.2)'), // lighter background
                            borderWidth: 2,
                            tension: 0.4, // Smooth line
                            fill: true,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Time'
                                },
                                // Only show a few labels for clarity
                                ticks: {
                                    autoSkip: true,
                                    maxTicksLimit: 10
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: config.label
                                },
                                beginAtZero: false
                            }
                        },
                        plugins: {
                            legend: {
                                display: true
                            }
                        }
                    }
                });
            }

        } catch (error) {
            console.error(`Error fetching ${sensorType} data:`, error);
        }
    }
    /**
     * Updates the chart appearance (axes, grid, text colors) based on the current theme.
     */
    function updateChartAppearance(chartInstance, sensorType) {
        const isDark = body.classList.contains('dark-theme');
        const config = sensorConfigs[sensorType];

        const textColor = isDark ? '#f8f9fa' : '#212529'; // White or Black
        const mutedColor = isDark ? '#adb5bd' : '#6c757d'; // Light Grey or Muted Grey
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

        chartInstance.options.color = textColor;

        // X-Axis Updates
        chartInstance.options.scales.x.title.color = textColor;
        chartInstance.options.scales.x.ticks.color = mutedColor;
        chartInstance.options.scales.x.grid.color = gridColor;

        // Y-Axis Updates
        chartInstance.options.scales.y.title.color = textColor;
        chartInstance.options.scales.y.ticks.color = mutedColor;
        chartInstance.options.scales.y.grid.color = gridColor;

        // Legend Updates
        chartInstance.options.plugins.legend.labels.color = textColor;
    }

    /**
    * Updates the chart and the last reading card for a specific sensor.
    */
    async function updateSensorData(sensorType) {
        const config = sensorConfigs[sensorType];

        try {
            const response = await fetch(config.endpoint);
            const data = await response.json();

            // The data is ordered DESC by timestamp, so the first element is the latest
            const latestReading = data[0];

            // 1. Update the 'Real-time' card
            if (latestReading) {
                document.getElementById(config.cardValueId).textContent = latestReading.value.toFixed(2);
                document.getElementById(config.cardTimeId).textContent = 'Last updated: ' + new Date(latestReading.timestamp).toLocaleTimeString();
            }

            // Reverse the data so it's chronologically ordered for the chart
            data.reverse();

            // Extract timestamps for X-axis (labels) and values for Y-axis
            const timestamps = data.map(item => new Date(item.timestamp).toLocaleTimeString());
            const values = data.map(item => item.value);

            // 2. Update the Chart
            if (charts[sensorType]) {
                // Update existing chart
                charts[sensorType].data.labels = timestamps;
                charts[sensorType].data.datasets[0].data = values;
                // NOTE: No need to call update() here, as updateAllData will call it after initialization. 
                // However, keeping update() here is harmless and ensures data refresh.
                charts[sensorType].update();
            } else {
                // Initialize the chart
                const ctx = document.getElementById(config.chartId).getContext('2d');
                charts[sensorType] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: timestamps,
                        datasets: [{
                            label: config.label,
                            data: values,
                            borderColor: config.color,
                            backgroundColor: config.color.replace('1)', '0.2)'), // lighter background
                            borderWidth: 2,
                            tension: 0.4, // Smooth line
                            fill: true,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        // Minimal options here. Colors/Text are set by updateChartAppearance.
                        scales: {
                            x: {
                                title: { display: true, text: 'Time' },
                                ticks: { autoSkip: true, maxTicksLimit: 10 }
                            },
                            y: {
                                title: { display: true, text: config.label },
                                beginAtZero: false
                            }
                        },
                        plugins: {
                            legend: { display: true }
                        }
                    }
                });
                // 🚨 THIS IS THE KEY CHANGE: Set initial colors based on the current theme
                updateChartAppearance(charts[sensorType], sensorType);
            }

        } catch (error) {
            console.error(`Error fetching ${sensorType} data:`, error);
        }
    }

    /**
    * Fetches and displays the latest server actions/logs.
    */
    async function updateActionLog() {
        try {
            const response = await fetch('/actions/latest');
            const logs = await response.json();
            const actionList = document.getElementById('action-list');

            if (!actionList) {
                console.error("Action log list element not found.");
                return;
            }

            actionList.innerHTML = ''; // Clear existing logs

            logs.forEach(log => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item theme-card d-flex justify-content-between';

                // Format time and message
                const time = new Date(log.timestamp).toLocaleTimeString();
                listItem.innerHTML = `
                <span>${log.message}</span>
                <small class="text-muted">${time}</small>
            `;
                actionList.appendChild(listItem);
            });

        } catch (error) {
            console.error("Error fetching action log:", error);
        }
    }


    /**
 * Fetches and displays the current state of controlled devices.
 */
    async function updateDeviceStates() {
        try {
            const response = await fetch('/states');
            const states = await response.json();

            // Map of device_id to the HTML element IDs
            const stateMap = {
                'ac': { valueId: 'ac-state', timeId: 'ac-updated' },
                'dehumidifier': { valueId: 'dehumidifier-state', timeId: 'dehumidifier-updated' },
                'light': { valueId: 'light-state', timeId: 'light-updated' }
            };

            for (const [deviceId, data] of Object.entries(states)) {
                const map = stateMap[deviceId];
                if (map) {
                    const valueEl = document.getElementById(map.valueId);
                    const timeEl = document.getElementById(map.timeId);

                    if (valueEl) valueEl.textContent = data.value;
                    if (timeEl) timeEl.textContent = 'Updated: ' + new Date(data.updated).toLocaleTimeString();
                }
            }

        } catch (error) {
            console.error("Error fetching device states:", error);
        }
    }
    /**
     * Main function to update all data.
     */
    function updateAllData() {
        Object.keys(sensorConfigs).forEach(updateSensorData);

        updateActionLog();

        updateDeviceStates(); 
    }

    // Attach click listener - This MUST execute last
    if (toggleButton) { // Add a check to confirm the element was found
        toggleButton.addEventListener('click', toggleTheme);
    } else {
        console.error("Theme toggle button with ID 'theme-toggle' not found.");
    }

    // Run the initial update and then set up a refresh interval (e.g., every 5 seconds)
    updateAllData();
    setInterval(updateAllData, 5000); // Poll the server every 5 seconds
});