// Chart management functionality
class ChartManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
        this.chart = null;
        this.cumulativeData = null;
    }

    createChartToggle() {
        const chartContainer = document.querySelector('.chart-container');
        
        // Remove existing toggle if present
        const existingToggle = document.getElementById('chart-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }

        // Create toggle buttons
        const toggleContainer = document.createElement('div');
        toggleContainer.id = 'chart-toggle';
        toggleContainer.className = 'chart-toggle';
        toggleContainer.innerHTML = `
            <div class="chart-controls-wrapper">
                <div class="toggle-buttons">
                    <button id="individual-chart-btn" class="toggle-btn active">
                        <i class="fas fa-chart-line"></i> Individual Funds
                    </button>
                    <button id="cumulative-chart-btn" class="toggle-btn">
                        <i class="fas fa-chart-area"></i> Portfolio vs Nifty 50
                    </button>
                </div>
                <div class="zoom-controls">
                    <button id="zoom-in-btn" class="zoom-btn" title="Zoom In">
                        <i class="fas fa-search-plus"></i>
                    </button>
                    <button id="zoom-out-btn" class="zoom-btn" title="Zoom Out">
                        <i class="fas fa-search-minus"></i>
                    </button>
                    <button id="reset-zoom-btn" class="zoom-btn" title="Reset Zoom">
                        <i class="fas fa-expand-arrows-alt"></i>
                    </button>
                    <button id="pan-btn" class="zoom-btn" title="Pan Mode">
                        <i class="fas fa-hand-rock"></i>
                    </button>
                </div>
            </div>
        `;

        // Insert toggle before chart canvas
        chartContainer.insertBefore(toggleContainer, chartContainer.firstChild);

        // Add event listeners for chart type toggle
        document.getElementById('individual-chart-btn').addEventListener('click', () => {
            this.switchToIndividualChart();
        });

        document.getElementById('cumulative-chart-btn').addEventListener('click', () => {
            this.switchToCumulativeChart();
        });

        // Add event listeners for zoom controls
        document.getElementById('zoom-in-btn').addEventListener('click', () => {
            this.zoomIn();
        });

        document.getElementById('zoom-out-btn').addEventListener('click', () => {
            this.zoomOut();
        });

        document.getElementById('reset-zoom-btn').addEventListener('click', () => {
            this.resetZoom();
        });

        document.getElementById('pan-btn').addEventListener('click', () => {
            this.togglePanMode();
        });
    }

    createPerformanceChart(funds) {
        const ctx = document.getElementById('performance-chart').getContext('2d');

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        this.hideChartLoading();

        // Prepare data for chart
        const datasets = [];
        const colors = ['#667eea', '#48bb78', '#ed8936', '#e53e3e', '#38b2ac'];

        funds.forEach((fund, index) => {
            if (fund.monthly_data && fund.monthly_data.length > 0) {
                datasets.push({
                    label: fund.fund_name,
                    data: fund.monthly_data.map(item => ({
                        x: item.date,
                        y: item.current_value
                    })),
                    borderColor: colors[index % colors.length],
                    backgroundColor: colors[index % colors.length] + '20',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 1,
                    pointHoverRadius: 5
                });

                // Add invested line for comparison (only once)
                if (index === 0) {
                    datasets.push({
                        label: 'Total Invested',
                        data: fund.monthly_data.map(item => ({
                            x: item.date,
                            y: item.invested
                        })),
                        borderColor: '#a0aec0',
                        backgroundColor: '#a0aec020',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        borderWidth: 1,
                        pointRadius: 0
                    });
                }
            }
        });

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 800,
                    easing: 'easeInOutQuart'
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yy'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Value (₹)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                plugins: {
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                                speed: 0.1
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy'
                        },
                        pan: {
                            enabled: false,
                            mode: 'xy',
                            threshold: 10
                        },
                        limits: {
                            y: {min: 0, max: 'original'},
                            x: {min: 'original', max: 'original'}
                        }
                    },
                    title: {
                        display: true,
                        text: 'Individual Fund Performance Over Time',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            },
            plugins: [window.ChartZoom]
        });
    }

    async fetchAndDisplayCumulativeChart() {
        try {
            const requestData = {
                funds: this.sipSimulator.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };

            console.log('Fetching cumulative performance data...');
            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/cumulative-performance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Cumulative performance result:', result);

            if (result.success) {
                this.createCumulativePerformanceChart(result.data);
            } else {
                console.error('Failed to fetch cumulative performance:', result.error);
                this.sipSimulator.showError('Could not load cumulative performance chart.');
            }
        } catch (error) {
            console.error('Error fetching cumulative performance:', error);
            this.sipSimulator.showError('Failed to load cumulative performance chart. Please try again.');
        }
    }

    createCumulativePerformanceChart(data) {
        const ctx = document.getElementById('performance-chart').getContext('2d');

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        this.hideChartLoading();

        // Prepare datasets for cumulative portfolio vs Nifty 50
        const datasets = [];

        // Portfolio data
        if (data.portfolio && data.portfolio.length > 0) {
            datasets.push({
                label: `Your Portfolio (${data.metadata.fund_count} funds)`,
                data: data.portfolio.map(item => ({
                    x: item.date,
                    y: item.current_value
                })),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: false,
                tension: 0.3,
                borderWidth: 3,
                pointRadius: 2,
                pointHoverRadius: 6
            });

            // Add invested line for portfolio
            datasets.push({
                label: 'Total Invested',
                data: data.portfolio.map(item => ({
                    x: item.date,
                    y: item.invested
                })),
                borderColor: '#a0aec0',
                backgroundColor: 'rgba(160, 174, 192, 0.1)',
                borderDash: [5, 5],
                fill: false,
                tension: 0.3,
                borderWidth: 2,
                pointRadius: 1,
                pointHoverRadius: 4
            });
        }

        // Nifty 50 data
        if (data.nifty50 && data.nifty50.length > 0) {
            datasets.push({
                label: 'Nifty 50 Index',
                data: data.nifty50.map(item => ({
                    x: item.date,
                    y: item.current_value
                })),
                borderColor: '#e53e3e',
                backgroundColor: 'rgba(229, 62, 62, 0.1)',
                fill: false,
                tension: 0.3,
                borderWidth: 3,
                pointRadius: 2,
                pointHoverRadius: 6
            });
        }

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yy'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Value (₹)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                plugins: {
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                                speed: 0.1
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy'
                        },
                        pan: {
                            enabled: false,
                            mode: 'xy',
                            threshold: 10
                        },
                        limits: {
                            y: {min: 0, max: 'original'},
                            x: {min: 'original', max: 'original'}
                        }
                    },
                    title: {
                        display: true,
                        text: 'Cumulative Portfolio Performance vs Nifty 50',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString();
                            },
                            afterLabel: function(context) {
                                // Calculate return percentage
                                const datasets = context.chart.data.datasets;
                                const investedDataset = datasets.find(ds => ds.label === 'Total Invested');
                                if (investedDataset && context.dataset.label !== 'Total Invested') {
                                    const investedValue = investedDataset.data[context.dataIndex]?.y;
                                    if (investedValue && investedValue > 0) {
                                        const currentValue = context.parsed.y;
                                        const returnPct = ((currentValue - investedValue) / investedValue * 100).toFixed(2);
                                        return `Return: ${returnPct}%`;
                                    }
                                }
                                return '';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            },
            plugins: [window.ChartZoom]
        });

        // Add performance summary
        this.displayCumulativePerformanceSummary(data);
    }

    switchToIndividualChart() {
        // Update button states
        document.getElementById('individual-chart-btn').classList.add('active');
        document.getElementById('cumulative-chart-btn').classList.remove('active');

        // Create individual funds chart
        if (this.sipSimulator.currentFundData) {
            this.createPerformanceChart(this.sipSimulator.currentFundData);
        }

        // Hide cumulative summary
        const cumulativeSummary = document.getElementById('cumulative-summary');
        if (cumulativeSummary) {
            cumulativeSummary.style.display = 'none';
        }
    }

    switchToCumulativeChart() {
        // Update button states
        document.getElementById('cumulative-chart-btn').classList.add('active');
        document.getElementById('individual-chart-btn').classList.remove('active');

        // Show loading state
        this.showChartLoading();

        // Create cumulative chart
        if (this.cumulativeData) {
            this.createCumulativePerformanceChart(this.cumulativeData);
        } else {
            // Fetch cumulative data if not already available
            this.fetchAndDisplayCumulativeChart();
        }
    }

    showChartLoading() {
        const ctx = document.getElementById('performance-chart').getContext('2d');
        if (this.chart) {
            this.chart.destroy();
        }

        // Show loading message
        const chartContainer = document.querySelector('.chart-container');
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'chart-loading';
        loadingDiv.className = 'chart-loading';
        loadingDiv.innerHTML = `
            <div class="chart-spinner"></div>
            <p>Loading cumulative performance chart...</p>
        `;

        const canvas = document.getElementById('performance-chart');
        canvas.style.display = 'none';
        chartContainer.appendChild(loadingDiv);
    }

    hideChartLoading() {
        const loadingDiv = document.getElementById('chart-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
        const canvas = document.getElementById('performance-chart');
        canvas.style.display = 'block';
    }

    async fetchCumulativeDataForChart() {
        try {
            const requestData = {
                funds: this.sipSimulator.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };

            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/cumulative-performance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.cumulativeData = result.data;
                }
            }
        } catch (error) {
            console.error('Error pre-fetching cumulative data:', error);
        }
    }

    displayCumulativePerformanceSummary(data) {
        // Create a summary section for cumulative performance
        const summaryContainer = document.getElementById('cumulative-summary') || this.createCumulativeSummaryContainer();
        
        if (data.portfolio.length > 0 && data.nifty50.length > 0) {
            const portfolioFinal = data.portfolio[data.portfolio.length - 1];
            const niftyFinal = data.nifty50[data.nifty50.length - 1];
            
            const portfolioReturn = ((portfolioFinal.current_value - portfolioFinal.invested) / portfolioFinal.invested * 100).toFixed(2);
            const niftyReturn = ((niftyFinal.current_value - niftyFinal.invested) / niftyFinal.invested * 100).toFixed(2);
            const outperformance = (parseFloat(portfolioReturn) - parseFloat(niftyReturn)).toFixed(2);
            
            summaryContainer.innerHTML = `
                <h3>Portfolio vs Nifty 50 Comparison</h3>
                <div class="comparison-metrics">
                    <div class="metric-card">
                        <h4>Your Portfolio</h4>
                        <div class="metric-value ${portfolioReturn >= 0 ? 'positive' : 'negative'}">
                            ${portfolioReturn}%
                        </div>
                        <div class="metric-label">Total Return</div>
                    </div>
                    <div class="metric-card">
                        <h4>Nifty 50 Index</h4>
                        <div class="metric-value ${niftyReturn >= 0 ? 'positive' : 'negative'}">
                            ${niftyReturn}%
                        </div>
                        <div class="metric-label">Total Return</div>
                    </div>
                    <div class="metric-card ${outperformance >= 0 ? 'outperform' : 'underperform'}">
                        <h4>Outperformance</h4>
                        <div class="metric-value">
                            ${outperformance >= 0 ? '+' : ''}${outperformance}%
                        </div>
                        <div class="metric-label">vs Nifty 50</div>
                    </div>
                </div>
            `;
        }
    }

    createCumulativeSummaryContainer() {
        const resultsSection = document.getElementById('results-section');
        const summaryContainer = document.createElement('div');
        summaryContainer.id = 'cumulative-summary';
        summaryContainer.className = 'cumulative-summary';
        
        // Insert after portfolio summary
        const portfolioSummary = document.getElementById('portfolio-summary').parentElement;
        portfolioSummary.insertAdjacentElement('afterend', summaryContainer);
        
        return summaryContainer;
    }

    // Zoom control methods
    zoomIn() {
        if (this.chart) {
            this.chart.zoom(1.1);
        }
    }

    zoomOut() {
        if (this.chart) {
            this.chart.zoom(0.9);
        }
    }

    resetZoom() {
        if (this.chart) {
            this.chart.resetZoom();
        }
    }

    togglePanMode() {
        if (this.chart) {
            const panBtn = document.getElementById('pan-btn');
            const isActive = panBtn.classList.contains('active');
            
            if (isActive) {
                // Disable pan mode
                this.chart.options.plugins.zoom.pan.enabled = false;
                panBtn.classList.remove('active');
                panBtn.title = 'Pan Mode';
            } else {
                // Enable pan mode
                this.chart.options.plugins.zoom.pan.enabled = true;
                panBtn.classList.add('active');
                panBtn.title = 'Pan Mode (Active)';
            }
            
            this.chart.update('none');
        }
    }
}

// Add chart methods to SIPSimulator prototype
SIPSimulator.prototype.createChartToggle = function() {
    if (!this.chartManager) {
        this.chartManager = new ChartManager(this);
    }
    return this.chartManager.createChartToggle();
};

SIPSimulator.prototype.createPerformanceChart = function(funds) {
    if (!this.chartManager) {
        this.chartManager = new ChartManager(this);
    }
    return this.chartManager.createPerformanceChart(funds);
};

SIPSimulator.prototype.fetchCumulativeDataForChart = function() {
    if (!this.chartManager) {
        this.chartManager = new ChartManager(this);
    }
    return this.chartManager.fetchCumulativeDataForChart();
}; 