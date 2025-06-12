// SIP simulation functionality
class SimulationManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
    }

    async simulateSIP() {
        if (this.sipSimulator.isSimulating) return;
        
        console.log('simulateSIP called');
        console.log('Selected funds:', this.sipSimulator.selectedFunds);
        console.log('Validation result:', this.sipSimulator.validateInputs());
        
        if (!this.sipSimulator.validateInputs()) return;

        this.sipSimulator.isSimulating = true;
        this.sipSimulator.showButtonLoading('simulate-btn', 'Simulating...');
        this.showProgressiveLoading();

        try {
            const requestData = {
                funds: this.sipSimulator.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };
            
            console.log('Request data:', requestData);
            
            // Update progress
            this.updateLoadingProgress('Fetching fund data...', 25);

            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Response result:', result);
            
            // Update progress
            this.updateLoadingProgress('Processing portfolio data...', 50);

            if (result.success) {
                console.log('Displaying results...');
                this.displayResults(result.data);
                
                // Update progress
                this.updateLoadingProgress('Complete!', 100);
                setTimeout(() => this.sipSimulator.hideLoading(), 500);
            } else {
                console.log('Simulation failed:', result.error);
                this.sipSimulator.showError(result.error || 'Simulation failed');
            }
        } catch (error) {
            console.error('Simulation error details:', error);
            
            let errorMessage = 'Failed to simulate SIP.';
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to server. Please ensure the backend is running on port 5000.';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = `Server error: ${error.message}`;
            } else {
                errorMessage = `Error: ${error.message}`;
            }
            
            this.sipSimulator.showError(errorMessage);
        } finally {
            this.sipSimulator.isSimulating = false;
            this.sipSimulator.hideButtonLoading('simulate-btn', '<i class="fas fa-calculator"></i> Simulate SIP');
            this.sipSimulator.hideLoading();
        }
    }

    showProgressiveLoading() {
        const loadingModal = document.getElementById('loading-modal');
        const loadingText = document.getElementById('loading-text') || this.createLoadingTextElement();
        const progressBar = document.getElementById('progress-bar') || this.createProgressBarElement();
        
        loadingModal.style.display = 'flex';
        this.updateLoadingProgress('Initializing...', 0);
    }

    createLoadingTextElement() {
        const loadingContent = document.querySelector('#loading-modal .modal-content');
        const textElement = document.createElement('div');
        textElement.id = 'loading-text';
        textElement.style.marginTop = '10px';
        textElement.style.color = '#4a5568';
        loadingContent.appendChild(textElement);
        return textElement;
    }

    createProgressBarElement() {
        const loadingContent = document.querySelector('#loading-modal .modal-content');
        const progressContainer = document.createElement('div');
        progressContainer.style.width = '100%';
        progressContainer.style.height = '6px';
        progressContainer.style.backgroundColor = '#e2e8f0';
        progressContainer.style.borderRadius = '3px';
        progressContainer.style.marginTop = '15px';
        progressContainer.style.overflow = 'hidden';
        
        const progressBar = document.createElement('div');
        progressBar.id = 'progress-bar';
        progressBar.style.height = '100%';
        progressBar.style.backgroundColor = '#667eea';
        progressBar.style.width = '0%';
        progressBar.style.transition = 'width 0.3s ease';
        
        progressContainer.appendChild(progressBar);
        loadingContent.appendChild(progressContainer);
        return progressBar;
    }

    updateLoadingProgress(text, percentage) {
        const loadingText = document.getElementById('loading-text');
        const progressBar = document.getElementById('progress-bar');
        
        if (loadingText) loadingText.textContent = text;
        if (progressBar) progressBar.style.width = `${percentage}%`;
    }

    displayResults(data) {
        // Show results section
        document.getElementById('results-section').style.display = 'block';
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

        // Display portfolio summary
        this.displayPortfolioSummary(data.portfolio_summary);

        // Display fund performance
        this.displayFundPerformance(data.funds);

        // Store the fund data for chart switching
        this.sipSimulator.currentFundData = data.funds;

        // Create chart toggle buttons
        this.createChartToggle();

        // Create default performance chart (individual funds)
        this.createPerformanceChart(data.funds);

        // Fetch cumulative data for later use
        this.fetchCumulativeDataForChart();
    }

    displayPortfolioSummary(summary) {
        const container = document.getElementById('portfolio-summary');
        container.innerHTML = `
            <div class="metric">
                <span class="metric-label">Total Invested:</span>
                <span class="metric-value">₹${summary.total_invested.toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Current Value:</span>
                <span class="metric-value">₹${summary.final_value.toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Absolute Return:</span>
                <span class="metric-value ${summary.absolute_return >= 0 ? 'positive' : 'negative'}">
                    ${summary.absolute_return.toFixed(2)}%
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">CAGR:</span>
                <span class="metric-value ${summary.cagr >= 0 ? 'positive' : 'negative'}">
                    ${summary.cagr.toFixed(2)}%
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">XIRR:</span>
                <span class="metric-value ${summary.xirr && summary.xirr >= 0 ? 'positive' : 'negative'}">
                    ${summary.xirr ? summary.xirr.toFixed(2) + '%' : 'N/A'}
                </span>
            </div>
        `;
    }

    displayFundPerformance(funds) {
        const container = document.getElementById('fund-performance');
        container.innerHTML = '';

        funds.forEach(fund => {
            const fundElement = document.createElement('div');
            fundElement.className = 'fund-item';
            fundElement.innerHTML = `
                <h4>${fund.fund_name}</h4>
                <div class="fund-metrics">
                    <div>Invested: ₹${fund.invested.toLocaleString()}</div>
                    <div>Current: ₹${fund.current_value.toLocaleString()}</div>
                    <div>Return: <span class="${fund.return_pct >= 0 ? 'positive' : 'negative'}">${fund.return_pct.toFixed(2)}%</span></div>
                    <div>CAGR: <span class="${fund.cagr >= 0 ? 'positive' : 'negative'}">${fund.cagr.toFixed(2)}%</span></div>
                </div>
            `;
            container.appendChild(fundElement);
        });
    }

    createChartToggle() {
        // Use the chart manager
        this.sipSimulator.createChartToggle();
    }

    createPerformanceChart(funds) {
        // Use the chart manager
        this.sipSimulator.createPerformanceChart(funds);
    }

    fetchCumulativeDataForChart() {
        // Use the chart manager
        this.sipSimulator.fetchCumulativeDataForChart();
    }
}

// Add simulation methods to SIPSimulator prototype
SIPSimulator.prototype.simulateSIP = function() {
    if (!this.simulationManager) {
        this.simulationManager = new SimulationManager(this);
    }
    return this.simulationManager.simulateSIP();
}; 