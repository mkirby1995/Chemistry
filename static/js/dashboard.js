// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    const runButton = document.getElementById('run-simulation');
    const pauseButton = document.getElementById('pause-simulation');
    const speedInput = document.getElementById('sim-speed');
    const durationInput = document.getElementById('sim-duration');
    const visualizationSelect = document.getElementById('visualization-select');
    const logsContainer = document.getElementById('logs-container');

    let simulationData = null;
    let simulationInterval = null;
    let currentStep = 0;
    let isPaused = false;

    runButton.addEventListener('click', function() {
        isPaused = false;
        fetchSimulationData();
    });

    pauseButton.addEventListener('click', function() {
        isPaused = true;
    });

    function fetchSimulationData() {
        const formData = new FormData();
        formData.append('sim_speed', speedInput.value);
        formData.append('sim_duration', durationInput.value);

        fetch('/run_simulation', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            simulationData = data;
            currentStep = 0;
            startSimulation();
        });
    }

    function startSimulation() {
        if (simulationInterval) {
            clearInterval(simulationInterval);
        }
        simulationInterval = setInterval(updateVisualization, 500); // Adjust interval as needed
    }

    function updateVisualization() {
        if (isPaused || currentStep >= simulationData.hour.length) {
            clearInterval(simulationInterval);
            return;
        }

        const visualizationType = visualizationSelect.value;
        if (visualizationType === 'tank_levels') {
            plotTankLevels(currentStep);
        } else if (visualizationType === 'power_demand') {
            plotPowerDemand(currentStep);
        } else if (visualizationType === 'battery_level') {
            plotBatteryLevel(currentStep);
        } else if (visualizationType === 'production_metrics') {
            plotProductionMetrics(currentStep);
        } else if (visualizationType === 'environmental_conditions') {
            plotEnvironmentalConditions(currentStep);
        } else if (visualizationType === 'efficiency_metrics') {
            plotEfficiencyMetrics(currentStep);
        } else if (visualizationType === 'power_generation') {
            plotPowerGeneration(currentStep);
        }

        logsContainer.textContent += `Step ${currentStep}: Simulation running...\n`;
        logsContainer.scrollTop = logsContainer.scrollHeight;

        currentStep++;
    }

    function plotTankLevels(step) {
        const traceCO2 = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.CO2_level.slice(0, step),
            name: 'CO₂ Level',
            mode: 'lines'
        };
        const traceH2 = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.H2_level.slice(0, step),
            name: 'H₂ Level',
            mode: 'lines'
        };
        const data = [traceCO2, traceH2];
        const layout = {
            title: 'Storage Tank Levels Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Level (g)' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotPowerDemand(step) {
        const tracePower = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.power_demand.slice(0, step),
            name: 'Total Power Demand',
            mode: 'lines'
        };
        const data = [tracePower];
        const layout = {
            title: 'Power Demand Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Power Demand (kJ)' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotBatteryLevel(step) {
        const traceBattery = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.battery_level.slice(0, step),
            name: 'Battery Level',
            mode: 'lines'
        };
        const data = [traceBattery];
        const layout = {
            title: 'Battery Level Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Battery Level (kJ)' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotProductionMetrics(step) {
        const traceH2Produced = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.H2_produced.slice(0, step),
            name: 'H₂ Produced',
            mode: 'lines'
        };
        const traceO2Produced = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.O2_produced.slice(0, step),
            name: 'O₂ Produced',
            mode: 'lines'
        };
        const data = [traceH2Produced, traceO2Produced];
        const layout = {
            title: 'Production Metrics Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Production (g)' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotEnvironmentalConditions(step) {
        const traceTemp = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.internal_temp_c.slice(0, step),
            name: 'Internal Temperature (°C)',
            mode: 'lines'
        };
        const tracePressure = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.internal_pressure_pa.slice(0, step),
            name: 'Internal Pressure (Pa)',
            mode: 'lines'
        };
        const data = [traceTemp, tracePressure];
        const layout = {
            title: 'Environmental Conditions Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Value' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotEfficiencyMetrics(step) {
        const traceEfficiency = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.catalyst_efficiency.slice(0, step),
            name: 'Catalyst Efficiency',
            mode: 'lines'
        };
        const data = [traceEfficiency];
        const layout = {
            title: 'Catalyst Efficiency Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Efficiency' }
        };
        Plotly.newPlot('visualization', data, layout);
    }

    function plotPowerGeneration(step) {
        const traceSolar = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.solar_power_generated.slice(0, step),
            name: 'Solar Power Generated',
            mode: 'lines'
        };
        const traceNuclear = {
            x: simulationData.hour.slice(0, step),
            y: simulationData.nuclear_power_generated.slice(0, step),
            name: 'Nuclear Power Generated',
            mode: 'lines'
        };
        const data = [traceSolar, traceNuclear];
        const layout = {
            title: 'Power Generation Over Time',
            xaxis: { title: 'Time (hours)' },
            yaxis: { title: 'Power Generated (kJ)' }
        };
        Plotly.newPlot('visualization', data, layout);
    }
});
