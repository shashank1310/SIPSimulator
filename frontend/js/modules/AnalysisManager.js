// Analysis functionality (Risk Analysis, Goal Planning, Step-up SIP)
class AnalysisManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
    }

    async analyzeRisk() {
        if (this.sipSimulator.selectedFunds.length === 0) {
            this.sipSimulator.showError('Please select funds from the SIP Simulator tab first.');
            return;
        }

        this.sipSimulator.showButtonLoading('analyze-risk-btn', 'Analyzing Risk...');

        try {
            const requestData = {
                funds: this.sipSimulator.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };

            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/risk-analysis`, {
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
                this.sipSimulator.showError(result.error || 'Risk analysis failed');
            }
        } catch (error) {
            console.error('Risk analysis error:', error);
            this.sipSimulator.showError('Failed to analyze risk. Please try again.');
        } finally {
            this.sipSimulator.hideButtonLoading('analyze-risk-btn', '<i class="fas fa-chart-line"></i> Analyze Portfolio Risk');
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
        this.sipSimulator.showButtonLoading('calculate-goal-btn', 'Calculating...');

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

            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/goal-planning`, {
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
                this.sipSimulator.showError(result.error || 'Goal calculation failed');
            }
        } catch (error) {
            console.error('Goal calculation error:', error);
            this.sipSimulator.showError('Failed to calculate goal. Please try again.');
        } finally {
            this.sipSimulator.hideButtonLoading('calculate-goal-btn', '<i class="fas fa-calculator"></i> Calculate SIP Requirement');
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
        if (this.sipSimulator.selectedFunds.length === 0) {
            this.sipSimulator.showError('Please select funds from the SIP Simulator tab first.');
            return;
        }

        this.sipSimulator.showButtonLoading('simulate-step-up-btn', 'Simulating...');

        try {
            const requestData = {
                funds: this.sipSimulator.selectedFunds,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value,
                step_up_percentage: parseInt(document.getElementById('step-up-percentage').value)
            };

            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/step-up-sip`, {
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
                this.sipSimulator.showError(result.error || 'Step-up SIP simulation failed');
            }
        } catch (error) {
            console.error('Step-up SIP error:', error);
            this.sipSimulator.showError('Failed to simulate step-up SIP. Please try again.');
        } finally {
            this.sipSimulator.hideButtonLoading('simulate-step-up-btn', '<i class="fas fa-chart-line"></i> Simulate Step-up SIP');
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
}

// Add analysis methods to SIPSimulator prototype
SIPSimulator.prototype.analyzeRisk = function() {
    if (!this.analysisManager) {
        this.analysisManager = new AnalysisManager(this);
    }
    return this.analysisManager.analyzeRisk();
};

SIPSimulator.prototype.calculateGoal = function() {
    if (!this.analysisManager) {
        this.analysisManager = new AnalysisManager(this);
    }
    return this.analysisManager.calculateGoal();
};

SIPSimulator.prototype.simulateStepUpSIP = function() {
    if (!this.analysisManager) {
        this.analysisManager = new AnalysisManager(this);
    }
    return this.analysisManager.simulateStepUpSIP();
}; 