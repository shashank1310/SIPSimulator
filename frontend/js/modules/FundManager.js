// Fund search and management functionality
class FundManager {
    constructor(sipSimulator) {
        this.sipSimulator = sipSimulator;
    }

    async searchFunds() {
        const query = document.getElementById('fund-search').value.trim();
        const resultsContainer = document.getElementById('search-results');

        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`${this.sipSimulator.apiBaseUrl}/search-funds?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            this.displaySearchResults(data.funds);
        } catch (error) {
            console.error('Error searching funds:', error);
            this.sipSimulator.showError('Failed to search funds. Please try again.');
        }
    }

    displaySearchResults(funds) {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '';

        if (funds.length === 0) {
            resultsContainer.innerHTML = '<div class="search-result-item">No funds found</div>';
        } else {
            funds.forEach(fund => {
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                resultItem.innerHTML = `
                    <strong>${fund.fund_name}</strong>
                    <br>
                    <small>Code: ${fund.scheme_code}</small>
                `;
                resultItem.addEventListener('click', () => this.addFund(fund));
                resultsContainer.appendChild(resultItem);
            });
        }

        resultsContainer.style.display = 'block';
    }

    addFund(fund) {
        // Check if fund already selected
        if (this.sipSimulator.selectedFunds.find(f => f.scheme_code === fund.scheme_code)) {
            this.sipSimulator.showError('This fund is already selected');
            return;
        }

        const fundData = {
            scheme_code: fund.scheme_code,
            fund_name: fund.fund_name,
            sip_amount: 10000 // Default amount
        };

        this.sipSimulator.selectedFunds.push(fundData);
        this.renderSelectedFunds();
        
        // Clear search
        document.getElementById('fund-search').value = '';
        document.getElementById('search-results').style.display = 'none';
    }

    renderSelectedFunds() {
        const container = document.getElementById('selected-funds');
        container.innerHTML = '';

        if (this.sipSimulator.selectedFunds.length === 0) {
            container.innerHTML = '<p style="color: #718096; text-align: center; padding: 20px;">No funds selected. Search and add funds to simulate your SIP.</p>';
            return;
        }

        this.sipSimulator.selectedFunds.forEach((fund, index) => {
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
        this.sipSimulator.selectedFunds[index].sip_amount = parseInt(amount);
    }

    removeFund(index) {
        this.sipSimulator.selectedFunds.splice(index, 1);
        this.renderSelectedFunds();
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
}

// Add fund management methods to SIPSimulator prototype
SIPSimulator.prototype.searchFunds = function() {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    return this.fundManager.searchFunds();
};

SIPSimulator.prototype.addFund = function(fund) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    this.fundManager.addFund(fund);
};

SIPSimulator.prototype.renderSelectedFunds = function() {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    this.fundManager.renderSelectedFunds();
};

SIPSimulator.prototype.updateFundAmount = function(index, amount) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    this.fundManager.updateFundAmount(index, amount);
};

SIPSimulator.prototype.removeFund = function(index) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    this.fundManager.removeFund(index);
};

SIPSimulator.prototype.getFundCategory = function(fundName) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    return this.fundManager.getFundCategory(fundName);
};

SIPSimulator.prototype.getFundRiskLevel = function(category) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    return this.fundManager.getFundRiskLevel(category);
};

SIPSimulator.prototype.getExpectedReturn = function(category) {
    if (!this.fundManager) {
        this.fundManager = new FundManager(this);
    }
    return this.fundManager.getExpectedReturn(category);
}; 