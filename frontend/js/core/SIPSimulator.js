// Main SIP Simulator class
class SIPSimulator {
    constructor() {
        this.selectedFunds = [];
        // Auto-detect API base URL based on environment
        this.apiBaseUrl = this.getApiBaseUrl();
        this.chart = null;
        this.isSimulating = false;
        this.searchTimeout = null;
        this.currentTheme = 'light';
        this.currentTab = 'simulator';
        this.currentFundData = null;
        this.cumulativeData = null;
        
        this.initializeEventListeners();
        this.initializeTheme();
        this.initializeNavigation();
        this.setDefaultDates();
        this.testBackendConnectivity();
    }

    getApiBaseUrl() {
        // If running on localhost, use localhost backend
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000/api';
        }
        // Otherwise, use the same domain (for Render deployment)
        return `${window.location.origin}/api`;
    }

    initializeEventListeners() {
        // Search functionality with improved debouncing
        document.getElementById('fund-search').addEventListener('input', 
            this.debounce(this.searchFunds.bind(this), 300));
        document.getElementById('search-btn').addEventListener('click', this.searchFunds.bind(this));

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

    async testBackendConnectivity() {
        try {
            console.log('Testing backend connectivity...');
            console.log('API Base URL:', this.apiBaseUrl);
            const healthUrl = this.apiBaseUrl.replace('/api', '/health');
            console.log('Health check URL:', healthUrl);
            
            const response = await fetch(healthUrl);
            const data = await response.json();
            console.log('✅ Backend connectivity test passed:', data);
        } catch (error) {
            console.error('❌ Backend connectivity test failed:', error);
            console.error('API Base URL:', this.apiBaseUrl);
            this.showError('Cannot connect to backend server. Please check your connection.');
        }
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').style.display = 'flex';
    }

    closeErrorModal() {
        document.getElementById('error-modal').style.display = 'none';
    }

    showLoading() {
        document.getElementById('loading-modal').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-modal').style.display = 'none';
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
} 