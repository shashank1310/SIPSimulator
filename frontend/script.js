class SIPSimulator {
    constructor() {
        this.selectedFunds = [];
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.chart = null;
        this.isSimulating = false;
        this.searchTimeout = null;
        this.currentTheme = 'light';
        this.currentTab = 'simulator';
        this.initializeEventListeners();
        this.initializeTheme();
        this.initializeNavigation();
        this.setDefaultDates();
        this.testBackendConnectivity();
    }

    initializeEventListeners() {
        // Search functionality with improved debouncing
        document.getElementById('fund-search').addEventListener('input', 
            this.debounce(this.searchFunds.bind(this), 200)); // Faster response
        document.getElementById('search-btn').addEventListener('click', this.searchFunds.bind(this));

        // Suggestion chips
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                document.getElementById('fund-search').value = query;
                this.searchFunds();
            });
        });

        // Analysis tabs
        document.querySelectorAll('.analysis-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const analysisType = e.target.getAttribute('data-analysis');
                this.switchAnalysisTab(analysisType);
            });
        });

        // Portfolio analyzer
        document.getElementById('add-holding-btn')?.addEventListener('click', this.addHolding.bind(this));
        document.getElementById('analyze-portfolio-btn')?.addEventListener('click', this.analyzePortfolio.bind(this));
        document.getElementById('portfolio-risk-btn')?.addEventListener('click', this.analyzePortfolioRisk.bind(this));
        document.getElementById('compare-funds-btn')?.addEventListener('click', this.compareFunds.bind(this));

        // Simulation buttons with loading state
        document.getElementById('simulate-btn').addEventListener('click', () => {
            if (!this.isSimulating) {
            console.log('Simulate button clicked!');
            this.simulateSIP();
            }
        });
        document.getElementById('benchmark-btn').addEventListener('click', () => {
            if (!this.isSimulating) {
                this.benchmarkSIP();
            }
        });

        // New feature buttons
        document.getElementById('analyze-risk-btn').addEventListener('click', () => {
            this.analyzeRisk();
        });

        document.getElementById('calculate-goal-btn').addEventListener('click', () => {
            this.calculateGoal();
        });

        document.getElementById('simulate-step-up-btn').addEventListener('click', () => {
            this.simulateStepUpSIP();
        });

        // Goal type change handler
        document.getElementById('goal-type').addEventListener('change', (e) => {
            this.handleGoalTypeChange(e.target.value);
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Modal close
        document.getElementById('close-error').addEventListener('click', this.closeErrorModal.bind(this));

        // Enter key for search
        document.getElementById('fund-search').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchFunds();
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', (event) => {
            const searchResults = document.getElementById('search-results');
            const searchContainer = document.querySelector('.search-container');
            
            if (!searchContainer.contains(event.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    initializeTheme() {
        // Check for saved theme preference or default to 'light'
        const savedTheme = localStorage.getItem('sip-simulator-theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        const themeIcon = document.querySelector('#theme-toggle i');
        if (theme === 'dark') {
            themeIcon.className = 'fas fa-sun';
        } else {
            themeIcon.className = 'fas fa-moon';
        }
        
        localStorage.setItem('sip-simulator-theme', theme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    initializeNavigation() {
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Update fund comparison if switching to that tab
        if (tabName === 'fund-comparison') {
            this.updateFundComparison();
        }
    }

    handleGoalTypeChange(goalType) {
        // Hide all goal-specific fields
        document.querySelectorAll('.goal-specific-fields').forEach(field => {
            field.style.display = 'none';
        });

        // Show relevant fields
        if (goalType === 'retirement') {
            document.getElementById('retirement-fields').style.display = 'block';
        } else if (goalType === 'education') {
            document.getElementById('education-fields').style.display = 'block';
        } else if (goalType === 'custom') {
            document.getElementById('custom-fields').style.display = 'block';
        }
    }

    async analyzeRisk() {
        if (this.selectedFunds.length === 0) {
            this.showError('Please select funds from the SIP Simulator tab first.');
            return;
        }

        this.showButtonLoading('analyze-risk-btn', 'Analyzing Risk...');

        try {
            const requestData = {
                funds: this.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };

            const response = await fetch(`${this.apiBaseUrl}/risk-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayRiskAnalysis(result.data);
            } else {
                this.showError(result.error || 'Risk analysis failed');
            }
        } catch (error) {
            console.error('Risk analysis error:', error);
            this.showError('Failed to analyze risk. Please try again.');
        } finally {
            this.hideButtonLoading('analyze-risk-btn', '<i class="fas fa-chart-line"></i> Analyze Portfolio Risk');
        }
    }

    displayRiskAnalysis(data) {
        const container = document.getElementById('risk-results');
        
        let html = `
            <div class="risk-analysis-header">
                <h3>Portfolio Risk Analysis</h3>
                <p>Analysis period: ${data.analysis_period.start_date} to ${data.analysis_period.end_date}</p>
            </div>

            <div class="risk-metrics-grid">
                <div class="risk-metric-card">
                    <h4>Annual Volatility</h4>
                    <div class="risk-metric-value risk-${this.getRiskLevel(data.portfolio_metrics.annualized_volatility, 'volatility')}">${data.portfolio_metrics.annualized_volatility}%</div>
                    <div class="risk-metric-label">Standard Deviation</div>
                </div>
                
                <div class="risk-metric-card">
                    <h4>Sharpe Ratio</h4>
                    <div class="risk-metric-value risk-${this.getRiskLevel(data.portfolio_metrics.sharpe_ratio, 'sharpe')}">${data.portfolio_metrics.sharpe_ratio}</div>
                    <div class="risk-metric-label">Risk-adjusted Return</div>
                </div>
                
                <div class="risk-metric-card">
                    <h4>Maximum Drawdown</h4>
                    <div class="risk-metric-value risk-${this.getRiskLevel(Math.abs(data.portfolio_metrics.max_drawdown), 'drawdown')}">${data.portfolio_metrics.max_drawdown}%</div>
                    <div class="risk-metric-label">Worst Loss Period</div>
                </div>
                
                <div class="risk-metric-card">
                    <h4>Sortino Ratio</h4>
                    <div class="risk-metric-value risk-${this.getRiskLevel(data.portfolio_metrics.sortino_ratio, 'sortino')}">${data.portfolio_metrics.sortino_ratio}</div>
                    <div class="risk-metric-label">Downside Risk Adjusted</div>
                </div>
                
                <div class="risk-metric-card">
                    <h4>Beta</h4>
                    <div class="risk-metric-value">${data.portfolio_metrics.beta}</div>
                    <div class="risk-metric-label">vs Nifty 50</div>
                </div>
                
                <div class="risk-metric-card">
                    <h4>Win Rate</h4>
                    <div class="risk-metric-value risk-${this.getRiskLevel(data.portfolio_metrics.win_rate, 'winrate')}">${data.portfolio_metrics.win_rate}%</div>
                    <div class="risk-metric-label">Positive Months</div>
                </div>
            </div>

            <div class="risk-comparison">
                <h4>Portfolio vs Benchmark Risk Metrics</h4>
                <div class="comparison-grid">
                    <div class="comparison-item">
                        <h5>Your Portfolio</h5>
                        <div class="comparison-value">Volatility: ${data.portfolio_metrics.annualized_volatility}%</div>
                        <div class="comparison-value">Sharpe: ${data.portfolio_metrics.sharpe_ratio}</div>
                    </div>
                    <div class="comparison-item">
                        <h5>Nifty 50 Benchmark</h5>
                        <div class="comparison-value">Volatility: ${data.benchmark_metrics.annualized_volatility}%</div>
                        <div class="comparison-value">Sharpe: ${data.benchmark_metrics.sharpe_ratio}</div>
                    </div>
                </div>
            </div>
        `;

        // Add individual fund risk metrics
        if (data.individual_funds.length > 1) {
            html += `
                <div class="individual-fund-risks">
                    <h4>Individual Fund Risk Metrics</h4>
                    <div class="fund-risk-grid">
            `;
            
            data.individual_funds.forEach(fund => {
                html += `
                    <div class="fund-risk-card">
                        <h5>${fund.fund_name}</h5>
                        <div class="fund-risk-metrics">
                            <div>Volatility: ${fund.risk_metrics.annualized_volatility}%</div>
                            <div>Sharpe: ${fund.risk_metrics.sharpe_ratio}</div>
                            <div>Max DD: ${fund.risk_metrics.max_drawdown}%</div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
        container.style.display = 'block';
    }

    getRiskLevel(value, metric) {
        switch (metric) {
            case 'volatility':
                return value > 20 ? 'high' : value > 15 ? 'medium' : 'low';
            case 'sharpe':
                return value > 1 ? 'low' : value > 0.5 ? 'medium' : 'high';
            case 'drawdown':
                return value > 20 ? 'high' : value > 10 ? 'medium' : 'low';
            case 'sortino':
                return value > 1 ? 'low' : value > 0.5 ? 'medium' : 'high';
            case 'winrate':
                return value > 60 ? 'low' : value > 50 ? 'medium' : 'high';
            default:
                return 'medium';
        }
    }

    async calculateGoal() {
        this.showButtonLoading('calculate-goal-btn', 'Calculating...');

        try {
            const goalType = document.getElementById('goal-type').value;
            const requestData = {
                goal_type: goalType,
                current_age: parseInt(document.getElementById('current-age').value),
                expected_return: parseFloat(document.getElementById('expected-return').value),
                inflation_rate: parseFloat(document.getElementById('inflation-rate').value)
            };

            // Add goal-specific data
            if (goalType === 'retirement') {
                requestData.retirement_age = parseInt(document.getElementById('retirement-age').value);
                requestData.monthly_expenses = parseInt(document.getElementById('monthly-expenses').value);
                requestData.years_after_retirement = 25; // Default
            } else if (goalType === 'education') {
                requestData.child_current_age = parseInt(document.getElementById('child-age').value);
                requestData.education_start_age = 18; // Default
                requestData.current_education_cost = parseInt(document.getElementById('education-cost').value);
            } else if (goalType === 'custom') {
                requestData.goal_amount = parseInt(document.getElementById('target-amount').value);
                requestData.time_horizon = parseInt(document.getElementById('time-horizon').value);
            }

            const response = await fetch(`${this.apiBaseUrl}/goal-planning`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayGoalResults(result.data);
            } else {
                this.showError(result.error || 'Goal calculation failed');
            }
        } catch (error) {
            console.error('Goal calculation error:', error);
            this.showError('Failed to calculate goal. Please try again.');
        } finally {
            this.hideButtonLoading('calculate-goal-btn', '<i class="fas fa-calculator"></i> Calculate SIP Requirement');
        }
    }

    displayGoalResults(data) {
        const container = document.getElementById('goal-results');
        
        const html = `
            <div class="goal-summary-grid">
                <div class="goal-summary-card">
                    <h3><i class="fas fa-bullseye"></i> Goal Summary</h3>
                    <div class="metric">
                        <span class="metric-label">Target Amount:</span>
                        <span class="metric-value">₹${data.goal_details.target_amount.toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Time Horizon:</span>
                        <span class="metric-value">${data.goal_details.time_horizon_years} years</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Expected Return:</span>
                        <span class="metric-value">${data.goal_details.expected_return}% p.a.</span>
                    </div>
                </div>

                <div class="goal-summary-card">
                    <h3><i class="fas fa-chart-line"></i> SIP Requirements</h3>
                    <div class="sip-comparison">
                        <div class="sip-option">
                            <h4>Regular SIP</h4>
                            <div class="sip-amount">₹${data.sip_requirements.regular_sip.toLocaleString()}</div>
                            <div class="sip-label">per month</div>
                        </div>
                        <div class="sip-option">
                            <h4>Step-up SIP</h4>
                            <div class="sip-amount step-up-value">₹${data.sip_requirements.step_up_sip.toLocaleString()}</div>
                            <div class="sip-label">starting amount</div>
                        </div>
                    </div>
                </div>

                <div class="goal-summary-card">
                    <h3><i class="fas fa-chart-pie"></i> Investment Projections</h3>
                    <div class="metric">
                        <span class="metric-label">Total Investment (Regular):</span>
                        <span class="metric-value">₹${data.sip_requirements.total_investment_regular.toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Returns:</span>
                        <span class="metric-value positive">₹${data.projections.total_returns.toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Wealth Multiplier:</span>
                        <span class="metric-value">${data.projections.wealth_multiplier}x</span>
                    </div>
                </div>

                <div class="goal-summary-card">
                    <h3><i class="fas fa-shield-alt"></i> Recommendations</h3>
                    <div class="metric">
                        <span class="metric-label">Risk Level:</span>
                        <span class="metric-value risk-${data.recommendations.risk_level.toLowerCase()}">${data.recommendations.risk_level}</span>
                    </div>
                    <div class="asset-allocation">
                        <h5>Recommended Allocation:</h5>
                        <div class="allocation-item">Equity: ${data.recommendations.asset_allocation.equity}%</div>
                        <div class="allocation-item">Debt: ${data.recommendations.asset_allocation.debt}%</div>
                        <div class="allocation-item">Gold: ${data.recommendations.asset_allocation.gold}%</div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
    }

    async simulateStepUpSIP() {
        if (this.selectedFunds.length === 0) {
            this.showError('Please select funds from the SIP Simulator tab first.');
            return;
        }

        this.showButtonLoading('simulate-step-up-btn', 'Simulating...');

        try {
            const requestData = {
                funds: this.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value,
                step_up_percentage: parseInt(document.getElementById('step-up-percentage').value)
            };

            const response = await fetch(`${this.apiBaseUrl}/step-up-sip`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayStepUpResults(result.data);
            } else {
                this.showError(result.error || 'Step-up SIP simulation failed');
            }
        } catch (error) {
            console.error('Step-up SIP error:', error);
            this.showError('Failed to simulate step-up SIP. Please try again.');
        } finally {
            this.hideButtonLoading('simulate-step-up-btn', '<i class="fas fa-chart-line"></i> Simulate Step-up SIP');
        }
    }

    displayStepUpResults(data) {
        const container = document.getElementById('step-up-results');
        
        let html = `
            <div class="step-up-comparison">
                <h3>Step-up SIP vs Regular SIP Comparison</h3>
                <div class="comparison-grid">
                    <div class="comparison-item">
                        <h4>Step-up SIP (${data.step_up_details.annual_increase}% annual increase)</h4>
                        <div class="comparison-value step-up-value">₹${data.portfolio_summary.final_value.toLocaleString()}</div>
                        <div class="comparison-label">Final Value</div>
                        <div class="comparison-value">₹${data.portfolio_summary.total_invested.toLocaleString()}</div>
                        <div class="comparison-label">Total Invested</div>
                        <div class="comparison-value positive">${data.portfolio_summary.absolute_return.toFixed(2)}%</div>
                        <div class="comparison-label">Total Return</div>
                    </div>
                    <div class="comparison-item">
                        <h4>Regular SIP</h4>
                        <div class="comparison-value regular-value">₹${data.comparison.regular_sip.final_value.toLocaleString()}</div>
                        <div class="comparison-label">Final Value</div>
                        <div class="comparison-value">₹${data.comparison.regular_sip.total_invested.toLocaleString()}</div>
                        <div class="comparison-label">Total Invested</div>
                        <div class="comparison-value">${data.comparison.regular_sip.return_percentage.toFixed(2)}%</div>
                        <div class="comparison-label">Total Return</div>
                    </div>
                </div>
                
                <div class="step-up-advantage">
                    <h4>Step-up SIP Advantage</h4>
                    <div class="advantage-value positive">
                        ₹${(data.portfolio_summary.final_value - data.comparison.regular_sip.final_value).toLocaleString()}
                    </div>
                    <div class="advantage-label">Additional wealth created</div>
                </div>
            </div>

            <div class="fund-wise-step-up">
                <h4>Fund-wise Step-up SIP Performance</h4>
                <div class="fund-step-up-grid">
        `;

        data.funds.forEach(fund => {
            html += `
                <div class="fund-step-up-card">
                    <h5>${fund.fund_name}</h5>
                    <div class="fund-step-up-metrics">
                        <div class="metric">
                            <span class="metric-label">Initial SIP:</span>
                            <span class="metric-value">₹${fund.initial_sip.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Final SIP:</span>
                            <span class="metric-value">₹${fund.final_sip.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Total Invested:</span>
                            <span class="metric-value">₹${fund.invested.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Current Value:</span>
                            <span class="metric-value">₹${fund.current_value.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Return:</span>
                            <span class="metric-value ${fund.return_pct >= 0 ? 'positive' : 'negative'}">${fund.return_pct.toFixed(2)}%</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
    }

    updateFundComparison() {
        const container = document.getElementById('comparison-results');
        
        if (this.selectedFunds.length === 0) {
            container.innerHTML = '<p class="placeholder-text">Select funds from the SIP Simulator tab to enable comparison.</p>';
            return;
        }

        let html = `
            <div class="comparison-header">
                <h3>Fund Comparison Analysis</h3>
                <p>Comparing ${this.selectedFunds.length} selected funds</p>
            </div>

            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Fund Name</th>
                        <th>Scheme Code</th>
                        <th>SIP Amount</th>
                        <th>Category</th>
                        <th>Risk Level</th>
                        <th>Expected Return</th>
                    </tr>
                </thead>
                <tbody>
        `;

        this.selectedFunds.forEach(fund => {
            // Mock additional fund data (in real implementation, fetch from API)
            const category = this.getFundCategory(fund.fund_name);
            const riskLevel = this.getFundRiskLevel(category);
            const expectedReturn = this.getExpectedReturn(category);

            html += `
                <tr>
                    <td class="fund-name-cell">${fund.fund_name}</td>
                    <td>${fund.scheme_code}</td>
                    <td>₹${fund.sip_amount.toLocaleString()}</td>
                    <td>${category}</td>
                    <td class="risk-${riskLevel.toLowerCase()}">${riskLevel}</td>
                    <td>${expectedReturn}%</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>

            <div class="comparison-insights">
                <h4>Portfolio Insights</h4>
                <div class="insights-grid">
                    <div class="insight-card">
                        <h5>Diversification Score</h5>
                        <div class="insight-value">${this.calculateDiversificationScore()}/10</div>
                    </div>
                    <div class="insight-card">
                        <h5>Average Risk Level</h5>
                        <div class="insight-value">${this.calculateAverageRisk()}</div>
                    </div>
                    <div class="insight-card">
                        <h5>Expected Portfolio Return</h5>
                        <div class="insight-value">${this.calculatePortfolioReturn()}%</div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    getFundCategory(fundName) {
        const name = fundName.toLowerCase();
        if (name.includes('large') || name.includes('bluechip')) return 'Large Cap';
        if (name.includes('mid')) return 'Mid Cap';
        if (name.includes('small')) return 'Small Cap';
        if (name.includes('multi') || name.includes('flexi')) return 'Multi Cap';
        if (name.includes('debt') || name.includes('bond')) return 'Debt';
        if (name.includes('hybrid')) return 'Hybrid';
        return 'Equity';
    }

    getFundRiskLevel(category) {
        const riskMap = {
            'Large Cap': 'Medium',
            'Mid Cap': 'High',
            'Small Cap': 'High',
            'Multi Cap': 'Medium',
            'Debt': 'Low',
            'Hybrid': 'Medium',
            'Equity': 'Medium'
        };
        return riskMap[category] || 'Medium';
    }

    getExpectedReturn(category) {
        const returnMap = {
            'Large Cap': '10-12',
            'Mid Cap': '12-15',
            'Small Cap': '15-18',
            'Multi Cap': '11-14',
            'Debt': '6-8',
            'Hybrid': '8-10',
            'Equity': '10-12'
        };
        return returnMap[category] || '10-12';
    }

    calculateDiversificationScore() {
        const categories = new Set(this.selectedFunds.map(fund => this.getFundCategory(fund.fund_name)));
        return Math.min(categories.size * 2, 10);
    }

    calculateAverageRisk() {
        const riskScores = this.selectedFunds.map(fund => {
            const risk = this.getFundRiskLevel(this.getFundCategory(fund.fund_name));
            return risk === 'Low' ? 1 : risk === 'Medium' ? 2 : 3;
        });
        const avgScore = riskScores.reduce((a, b) => a + b, 0) / riskScores.length;
        return avgScore <= 1.5 ? 'Low' : avgScore <= 2.5 ? 'Medium' : 'High';
    }

    calculatePortfolioReturn() {
        const totalSip = this.selectedFunds.reduce((sum, fund) => sum + fund.sip_amount, 0);
        let weightedReturn = 0;
        
        this.selectedFunds.forEach(fund => {
            const category = this.getFundCategory(fund.fund_name);
            const returnRange = this.getExpectedReturn(category);
            const avgReturn = returnRange.includes('-') ? 
                (parseInt(returnRange.split('-')[0]) + parseInt(returnRange.split('-')[1])) / 2 :
                parseInt(returnRange);
            const weight = fund.sip_amount / totalSip;
            weightedReturn += avgReturn * weight;
        });
        
        return weightedReturn.toFixed(1);
    }

    setDefaultDates() {
        const today = new Date();
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
        
        document.getElementById('end-date').value = today.toISOString().split('T')[0];
        document.getElementById('start-date').value = oneYearAgo.toISOString().split('T')[0];
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async searchFunds() {
        const query = document.getElementById('fund-search').value.trim();
        const resultsContainer = document.getElementById('search-results');
        const loadingIndicator = document.getElementById('search-loading');

        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        // Show loading
        loadingIndicator.style.display = 'block';
        resultsContainer.innerHTML = '';

        try {
            console.log('Searching for:', query);
            const response = await fetch(`${this.apiBaseUrl}/search-funds?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Search response:', data);

            this.displaySearchResults(data.funds || []);
        } catch (error) {
            console.error('Search error:', error);
            this.displaySearchError(error.message);
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    displaySearchResults(funds) {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '';

        if (!funds || funds.length === 0) {
            resultsContainer.innerHTML = '<div class="search-no-results">No funds found. Try different keywords like "HDFC", "SBI", or "Large Cap".</div>';
        } else {
            funds.slice(0, 10).forEach(fund => { // Limit to 10 results for performance
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                resultItem.innerHTML = `
                    <div class="search-result-main">
                        <strong>${fund.fund_name}</strong>
                        <small>Code: ${fund.scheme_code}</small>
                    </div>
                    <div class="search-result-meta">
                        <div>Click to add</div>
                    </div>
                `;
                resultItem.addEventListener('click', () => this.addFund(fund));
                resultsContainer.appendChild(resultItem);
            });
        }

        resultsContainer.style.display = 'block';
    }

    displaySearchError(errorMessage) {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-triangle"></i>
                Search failed: ${errorMessage}
                <br><small>Please check your connection and try again.</small>
            </div>
        `;
        resultsContainer.style.display = 'block';
    }

    addFund(fund) {
        // Check if fund already selected
        if (this.selectedFunds.find(f => f.scheme_code === fund.scheme_code)) {
            this.showError('This fund is already selected');
            return;
        }

        const fundData = {
            scheme_code: fund.scheme_code,
            fund_name: fund.fund_name,
            sip_amount: 10000 // Default amount
        };

        this.selectedFunds.push(fundData);
        this.renderSelectedFunds();
        
        // Clear search
        document.getElementById('fund-search').value = '';
        document.getElementById('search-results').style.display = 'none';
    }

    renderSelectedFunds() {
        const container = document.getElementById('selected-funds');
        container.innerHTML = '';

        if (this.selectedFunds.length === 0) {
            container.innerHTML = '<p style="color: #718096; text-align: center; padding: 20px;">No funds selected. Search and add funds to simulate your SIP.</p>';
            return;
        }

        this.selectedFunds.forEach((fund, index) => {
            const fundElement = document.createElement('div');
            fundElement.className = 'selected-fund';
            fundElement.innerHTML = `
                <div class="fund-info">
                    <h4>${fund.fund_name}</h4>
                    <p>Scheme Code: ${fund.scheme_code}</p>
                </div>
                <div class="fund-controls">
                    <label>Monthly SIP: ₹</label>
                    <input type="number" value="${fund.sip_amount}" min="500" step="500" 
                           onchange="sipSimulator.updateFundAmount(${index}, this.value)">
                    <button class="remove-fund" onclick="sipSimulator.removeFund(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(fundElement);
        });
    }

    updateFundAmount(index, amount) {
        this.selectedFunds[index].sip_amount = parseInt(amount);
    }

    removeFund(index) {
        this.selectedFunds.splice(index, 1);
        this.renderSelectedFunds();
    }

    validateInputs() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        console.log('Validating inputs:');
        console.log('Start date:', startDate);
        console.log('End date:', endDate);
        console.log('Selected funds count:', this.selectedFunds.length);

        if (!startDate || !endDate) {
            console.log('Validation failed: Missing dates');
            this.showError('Please select both start and end dates');
            return false;
        }

        if (new Date(startDate) >= new Date(endDate)) {
            console.log('Validation failed: Start date >= end date');
            this.showError('Start date must be before end date');
            return false;
        }

        if (this.selectedFunds.length === 0) {
            console.log('Validation failed: No funds selected');
            this.showError('Please select at least one fund');
            return false;
        }

        console.log('Validation passed');
        return true;
    }

    async simulateSIP() {
        if (this.isSimulating) return;
        
        console.log('simulateSIP called');
        console.log('Selected funds:', this.selectedFunds);
        console.log('Validation result:', this.validateInputs());
        
        if (!this.validateInputs()) return;

        this.isSimulating = true;
        this.showButtonLoading('simulate-btn', 'Simulating...');
        this.showProgressiveLoading();

        try {
            const requestData = {
                funds: this.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };
            
            console.log('Request data:', requestData);
            
            // Update progress
            this.updateLoadingProgress('Fetching fund data...', 25);

            const response = await fetch(`${this.apiBaseUrl}/simulate`, {
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
                setTimeout(() => this.hideLoading(), 500);
            } else {
                console.log('Simulation failed:', result.error);
                this.showError(result.error || 'Simulation failed');
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
            
            this.showError(errorMessage);
        } finally {
            this.isSimulating = false;
            this.hideButtonLoading('simulate-btn', '<i class="fas fa-calculator"></i> Simulate SIP');
            this.hideLoading();
        }
    }

    async fetchAndDisplayCumulativeChart() {
        try {
            // Validate that funds are selected
            if (!this.selectedFunds || this.selectedFunds.length === 0) {
                this.showError('Please select at least one fund to compare with Nifty 50.');
                return;
            }

            // Validate date inputs
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            
            if (!startDate || !endDate) {
                this.showError('Please select both start and end dates.');
                return;
            }

            if (new Date(startDate) >= new Date(endDate)) {
                this.showError('Start date must be before end date.');
                return;
            }

            const requestData = {
                funds: this.selectedFunds,
                start_date: startDate,
                end_date: endDate
            };

            console.log('Fetching cumulative performance data...', requestData);
            
            // Show loading state
            this.showChartLoading();
            
            const response = await fetch(`${this.apiBaseUrl}/cumulative-performance`, {
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

            if (result.success && result.data) {
                // Validate data structure
                if (!result.data.portfolio || !Array.isArray(result.data.portfolio) || result.data.portfolio.length === 0) {
                    throw new Error('Invalid portfolio data received from server');
                }
                
                if (!result.data.nifty50 || !Array.isArray(result.data.nifty50) || result.data.nifty50.length === 0) {
                    console.warn('No Nifty 50 data available, showing portfolio data only');
                }

                // Store data for future use
                this.cumulativeData = result.data;
                
                // Create the chart
                this.createCumulativePerformanceChart(result.data);
                
                // Show success message
                this.showSuccessMessage('Portfolio vs Nifty 50 comparison loaded successfully!');
            } else {
                console.error('Failed to fetch cumulative performance:', result.error);
                this.showError(result.error || 'Could not load cumulative performance chart.');
            }
        } catch (error) {
            console.error('Error fetching cumulative performance:', error);
            this.hideChartLoading();
            
            // Provide specific error messages
            if (error.message.includes('fetch')) {
                this.showError('Network error: Unable to connect to server. Please check your connection and try again.');
            } else if (error.message.includes('HTTP error')) {
                this.showError('Server error: Please try again later or contact support.');
            } else {
                this.showError(`Failed to load Portfolio vs Nifty 50 comparison: ${error.message}`);
            }
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

    createCumulativePerformanceChart(data) {
        const ctx = document.getElementById('performance-chart').getContext('2d');

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        this.hideChartLoading();

        // Validate input data
        if (!data) {
            this.showError('No data available for chart creation');
            return;
        }

        // Prepare datasets for cumulative portfolio vs Nifty 50
        const datasets = [];
        let hasValidData = false;

        // Portfolio data
        if (data.portfolio && Array.isArray(data.portfolio) && data.portfolio.length > 0) {
            // Validate portfolio data structure
            const validPortfolioData = data.portfolio.filter(item => 
                item && item.date && typeof item.current_value === 'number' && typeof item.invested === 'number'
            );

            if (validPortfolioData.length > 0) {
                hasValidData = true;
                
                datasets.push({
                    label: `Your Portfolio (${data.metadata?.fund_count || this.selectedFunds.length} funds)`,
                    data: validPortfolioData.map(item => ({
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
                    data: validPortfolioData.map(item => ({
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
        }

        // Nifty 50 data
        if (data.nifty50 && Array.isArray(data.nifty50) && data.nifty50.length > 0) {
            // Validate Nifty 50 data structure
            const validNiftyData = data.nifty50.filter(item => 
                item && item.date && typeof item.current_value === 'number'
            );

            if (validNiftyData.length > 0) {
                hasValidData = true;
                
                datasets.push({
                    label: 'Nifty 50 Index',
                    data: validNiftyData.map(item => ({
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
        }

        // Check if we have any valid data to display
        if (!hasValidData) {
            this.showError('No valid data available for Portfolio vs Nifty 50 comparison');
            return;
        }

        // Create chart with enhanced configuration
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
                                return '₹' + value.toLocaleString('en-IN');
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
                        text: 'Portfolio vs Nifty 50 Performance Comparison',
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
                                return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString('en-IN');
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
        
        // Show chart info
        console.log('Portfolio vs Nifty 50 chart created successfully with', datasets.length, 'datasets');
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

    async benchmarkSIP() {
        if (this.isSimulating) return;
        if (!this.validateInputs()) return;

        this.isSimulating = true;
        this.showButtonLoading('benchmark-btn', 'Comparing...');
        this.showLoading();

        try {
            // First run the regular simulation
            await this.simulateSIP();

            // Then get benchmark data
            const totalSipAmount = this.selectedFunds.reduce((sum, fund) => sum + fund.sip_amount, 0);
            
            const benchmarkData = {
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value,
                sip_amount: totalSipAmount
            };

            const response = await fetch(`${this.apiBaseUrl}/benchmark`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(benchmarkData)
            });

            const result = await response.json();
            this.hideLoading();

            if (result.success) {
                this.displayBenchmarkComparison(result.data);
            } else {
                this.showError(result.error || 'Benchmark comparison failed');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Benchmark error:', error);
            this.showError('Failed to get benchmark data. Please try again.');
        } finally {
            this.isSimulating = false;
            this.hideButtonLoading('benchmark-btn', '<i class="fas fa-chart-bar"></i> Compare with Nifty 50');
        }
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
        this.currentFundData = data.funds;

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

    switchToIndividualChart() {
        // Update button states
        document.getElementById('individual-chart-btn').classList.add('active');
        document.getElementById('cumulative-chart-btn').classList.remove('active');

        // Create individual funds chart
        if (this.currentFundData) {
            this.createPerformanceChart(this.currentFundData);
        }

        // Hide cumulative summary
        const cumulativeSummary = document.getElementById('cumulative-summary');
        if (cumulativeSummary) {
            cumulativeSummary.style.display = 'none';
        }
    }

    switchToCumulativeChart() {
        // Validate that funds are selected
        if (!this.selectedFunds || this.selectedFunds.length === 0) {
            this.showError('Please select at least one fund before switching to Portfolio vs Nifty 50 comparison.');
            // Switch back to individual chart
            document.getElementById('individual-chart-btn').classList.add('active');
            document.getElementById('cumulative-chart-btn').classList.remove('active');
            return;
        }

        // Validate date inputs
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        if (!startDate || !endDate) {
            this.showError('Please select both start and end dates before viewing Portfolio vs Nifty 50 comparison.');
            // Switch back to individual chart
            document.getElementById('individual-chart-btn').classList.add('active');
            document.getElementById('cumulative-chart-btn').classList.remove('active');
            return;
        }

        // Update button states
        document.getElementById('cumulative-chart-btn').classList.add('active');
        document.getElementById('individual-chart-btn').classList.remove('active');

        // Show loading state
        this.showChartLoading();

        // Create cumulative chart
        if (this.cumulativeData) {
            // Check if cached data is still valid
            const cachedStartDate = this.cumulativeData.metadata?.start_date;
            const cachedEndDate = this.cumulativeData.metadata?.end_date;
            const cachedFundCount = this.cumulativeData.metadata?.fund_count;
            
            if (cachedStartDate === startDate && 
                cachedEndDate === endDate && 
                cachedFundCount === this.selectedFunds.length) {
                // Use cached data
                console.log('Using cached cumulative data');
                this.createCumulativePerformanceChart(this.cumulativeData);
            } else {
                // Fetch fresh data
                console.log('Fetching fresh cumulative data due to parameter changes');
                this.fetchAndDisplayCumulativeChart();
            }
        } else {
            // Fetch cumulative data if not already available
            console.log('Fetching cumulative data for the first time');
            this.fetchAndDisplayCumulativeChart();
        }

        // Hide individual fund summary
        const cumulativeSummary = document.getElementById('cumulative-summary');
        if (cumulativeSummary) {
            cumulativeSummary.style.display = 'block';
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
                funds: this.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };

            const response = await fetch(`${this.apiBaseUrl}/cumulative-performance`, {
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

    displayBenchmarkComparison(benchmarkData) {
        const container = document.getElementById('benchmark-comparison');
        const dataContainer = document.getElementById('benchmark-data');
        
        const benchmark = benchmarkData.portfolio_summary;
        
        dataContainer.innerHTML = `
            <div class="metric">
                <span class="metric-label">Nifty 50 Invested:</span>
                <span class="metric-value">₹${benchmark.total_invested.toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Nifty 50 Current Value:</span>
                <span class="metric-value">₹${benchmark.final_value.toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Nifty 50 Return:</span>
                <span class="metric-value ${benchmark.absolute_return >= 0 ? 'positive' : 'negative'}">
                    ${benchmark.absolute_return.toFixed(2)}%
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Nifty 50 CAGR:</span>
                <span class="metric-value ${benchmark.cagr >= 0 ? 'positive' : 'negative'}">
                    ${benchmark.cagr.toFixed(2)}%
                </span>
            </div>
        `;
        
        container.style.display = 'block';
    }

    showLoading() {
        document.getElementById('loading-modal').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-modal').style.display = 'none';
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').style.display = 'flex';
    }

    closeErrorModal() {
        document.getElementById('error-modal').style.display = 'none';
    }

    async testBackendConnectivity() {
        try {
            console.log('Testing backend connectivity...');
            const response = await fetch(`${this.apiBaseUrl.replace('/api', '')}/`);
            const text = await response.text();
            console.log('✅ Backend connectivity test passed:', text);
        } catch (error) {
            console.error('❌ Backend connectivity test failed:', error);
            console.error('Please ensure the backend server is running on http://localhost:5000');
            this.showError('Cannot connect to backend server. Please ensure it is running on port 5000.');
        }
    }

    showButtonLoading(buttonId, loadingText = 'Processing...') {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <div class="button-spinner"></div>
                ${loadingText}
            `;
        }
    }

    hideButtonLoading(buttonId, originalText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
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

    showSuccessMessage(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    switchAnalysisTab(analysisType) {
        // Update active analysis tab
        document.querySelectorAll('.analysis-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-analysis="${analysisType}"]`).classList.add('active');

        // Update active analysis content
        document.querySelectorAll('.analysis-content').forEach(content => {
            content.classList.remove('active');
        });
        
        if (analysisType === 'risk') {
            document.getElementById('risk-analysis-content').classList.add('active');
        } else if (analysisType === 'comparison') {
            document.getElementById('comparison-content').classList.add('active');
            this.updateFundComparison();
        }
    }

    // Portfolio analyzer methods
    portfolioHoldings = [];

    addHolding() {
        const search = document.getElementById('holding-search').value.trim();
        const quantity = parseFloat(document.getElementById('holding-quantity').value);
        const price = parseFloat(document.getElementById('holding-price').value);

        if (!search || !quantity || !price) {
            this.showError('Please fill all fields to add a holding.');
            return;
        }

        const holding = {
            id: Date.now(),
            name: search,
            quantity: quantity,
            avgPrice: price,
            currentValue: quantity * price // Mock current value
        };

        this.portfolioHoldings.push(holding);
        this.renderPortfolioHoldings();
        
        // Clear form
        document.getElementById('holding-search').value = '';
        document.getElementById('holding-quantity').value = '';
        document.getElementById('holding-price').value = '';
    }

    renderPortfolioHoldings() {
        const container = document.getElementById('portfolio-holdings');
        container.innerHTML = '';

        if (this.portfolioHoldings.length === 0) {
            container.innerHTML = '<p class="placeholder-text">No holdings added yet. Add your stocks/funds to analyze your portfolio.</p>';
            return;
        }

        this.portfolioHoldings.forEach(holding => {
            const holdingElement = document.createElement('div');
            holdingElement.className = 'holding-item';
            
            const currentValue = holding.quantity * holding.avgPrice * (1 + (Math.random() * 0.4 - 0.2)); // Mock price change
            const pnl = currentValue - (holding.quantity * holding.avgPrice);
            const pnlPercent = (pnl / (holding.quantity * holding.avgPrice)) * 100;
            
            holdingElement.innerHTML = `
                <div class="holding-info">
                    <h4>${holding.name}</h4>
                    <p>Qty: ${holding.quantity} | Avg Price: ₹${holding.avgPrice.toFixed(2)}</p>
                </div>
                <div class="holding-metrics">
                    <div class="holding-metric">
                        <div class="holding-metric-label">Invested</div>
                        <div class="holding-metric-value">₹${(holding.quantity * holding.avgPrice).toLocaleString()}</div>
                    </div>
                    <div class="holding-metric">
                        <div class="holding-metric-label">Current</div>
                        <div class="holding-metric-value">₹${currentValue.toLocaleString()}</div>
                    </div>
                    <div class="holding-metric">
                        <div class="holding-metric-label">P&L</div>
                        <div class="holding-metric-value ${pnl >= 0 ? 'positive' : 'negative'}">
                            ${pnl >= 0 ? '+' : ''}₹${pnl.toLocaleString()} (${pnlPercent.toFixed(2)}%)
                        </div>
                    </div>
                </div>
                <div class="holding-actions">
                    <button class="btn-icon btn-edit" onclick="sipSimulator.editHolding(${holding.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="sipSimulator.removeHolding(${holding.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(holdingElement);
        });
    }

    removeHolding(id) {
        this.portfolioHoldings = this.portfolioHoldings.filter(h => h.id !== id);
        this.renderPortfolioHoldings();
    }

    editHolding(id) {
        const holding = this.portfolioHoldings.find(h => h.id === id);
        if (holding) {
            document.getElementById('holding-search').value = holding.name;
            document.getElementById('holding-quantity').value = holding.quantity;
            document.getElementById('holding-price').value = holding.avgPrice;
            this.removeHolding(id);
        }
    }

    async analyzePortfolio() {
        if (this.portfolioHoldings.length === 0) {
            this.showError('Please add holdings to analyze your portfolio.');
            return;
        }

        this.showButtonLoading('analyze-portfolio-btn', 'Analyzing...');
        
        // Mock portfolio analysis
        setTimeout(() => {
            const totalInvested = this.portfolioHoldings.reduce((sum, h) => sum + (h.quantity * h.avgPrice), 0);
            const totalCurrent = this.portfolioHoldings.reduce((sum, h) => sum + (h.quantity * h.avgPrice * (1 + (Math.random() * 0.4 - 0.2))), 0);
            const totalPnL = totalCurrent - totalInvested;
            const totalPnLPercent = (totalPnL / totalInvested) * 100;

            const resultsContainer = document.getElementById('portfolio-analysis-results');
            resultsContainer.innerHTML = `
                <div class="portfolio-summary-grid">
                    <div class="metric-card">
                        <h4>Total Invested</h4>
                        <div class="metric-value">₹${totalInvested.toLocaleString()}</div>
                    </div>
                    <div class="metric-card">
                        <h4>Current Value</h4>
                        <div class="metric-value">₹${totalCurrent.toLocaleString()}</div>
                    </div>
                    <div class="metric-card">
                        <h4>Total P&L</h4>
                        <div class="metric-value ${totalPnL >= 0 ? 'positive' : 'negative'}">
                            ${totalPnL >= 0 ? '+' : ''}₹${totalPnL.toLocaleString()} (${totalPnLPercent.toFixed(2)}%)
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.style.display = 'block';
            
            this.hideButtonLoading('analyze-portfolio-btn', '<i class="fas fa-chart-line"></i> Analyze Portfolio');
        }, 1500);
    }

    async analyzePortfolioRisk() {
        if (this.portfolioHoldings.length === 0) {
            this.showError('Please add holdings to analyze portfolio risk.');
            return;
        }

        this.showButtonLoading('portfolio-risk-btn', 'Analyzing Risk...');
        
        // Mock risk analysis
        setTimeout(() => {
            const resultsContainer = document.getElementById('portfolio-analysis-results');
            resultsContainer.innerHTML = `
                <div class="risk-metrics-grid">
                    <div class="risk-metric-card">
                        <h4>Portfolio Beta</h4>
                        <div class="risk-metric-value">${(0.8 + Math.random() * 0.6).toFixed(2)}</div>
                        <div class="risk-metric-label">vs Market</div>
                    </div>
                    <div class="risk-metric-card">
                        <h4>Volatility</h4>
                        <div class="risk-metric-value risk-medium">${(15 + Math.random() * 10).toFixed(1)}%</div>
                        <div class="risk-metric-label">Annual</div>
                    </div>
                    <div class="risk-metric-card">
                        <h4>Sharpe Ratio</h4>
                        <div class="risk-metric-value risk-low">${(0.5 + Math.random() * 1).toFixed(2)}</div>
                        <div class="risk-metric-label">Risk Adjusted</div>
                    </div>
                </div>
            `;
            resultsContainer.style.display = 'block';
            
            this.hideButtonLoading('portfolio-risk-btn', '<i class="fas fa-shield-alt"></i> Risk Analysis');
        }, 1500);
    }

    compareFunds() {
        if (this.selectedFunds.length === 0) {
            this.showError('Please select funds from the SIP Simulator first.');
            return;
        }
        this.updateFundComparison();
    }
}

// Initialize the application
const sipSimulator = new SIPSimulator(); 