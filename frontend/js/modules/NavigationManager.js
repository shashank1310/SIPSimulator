// Navigation and tab management functionality
class NavigationManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
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

        this.sipSimulator.currentTab = tabName;

        // Update fund comparison if switching to that tab
        if (tabName === 'fund-comparison') {
            this.sipSimulator.updateFundComparison();
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
}

// Add navigation methods to SIPSimulator prototype
SIPSimulator.prototype.initializeNavigation = function() {
    if (!this.navigationManager) {
        this.navigationManager = new NavigationManager(this);
    }
    this.navigationManager.initializeNavigation();
};

SIPSimulator.prototype.switchTab = function(tabName) {
    if (!this.navigationManager) {
        this.navigationManager = new NavigationManager(this);
    }
    this.navigationManager.switchTab(tabName);
};

SIPSimulator.prototype.handleGoalTypeChange = function(goalType) {
    if (!this.navigationManager) {
        this.navigationManager = new NavigationManager(this);
    }
    this.navigationManager.handleGoalTypeChange(goalType);
}; 