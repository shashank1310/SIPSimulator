// Theme management functionality
class ThemeManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
    }

    initializeTheme() {
        // Check for saved theme preference or default to 'light'
        const savedTheme = localStorage.getItem('sip-simulator-theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        this.sipSimulator.currentTheme = theme;
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
        const newTheme = this.sipSimulator.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
}

// Add theme methods to SIPSimulator prototype
SIPSimulator.prototype.initializeTheme = function() {
    if (!this.themeManager) {
        this.themeManager = new ThemeManager(this);
    }
    this.themeManager.initializeTheme();
};

SIPSimulator.prototype.setTheme = function(theme) {
    if (!this.themeManager) {
        this.themeManager = new ThemeManager(this);
    }
    this.themeManager.setTheme(theme);
};

SIPSimulator.prototype.toggleTheme = function() {
    if (!this.themeManager) {
        this.themeManager = new ThemeManager(this);
    }
    this.themeManager.toggleTheme();
}; 