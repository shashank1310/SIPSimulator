# 🚀 Advanced SIP Simulator

A comprehensive **Systematic Investment Plan (SIP) Simulator** with advanced analytics, risk assessment, goal-based planning, and modern UI features. Built with Flask (Python) backend and vanilla JavaScript frontend.

## ✨ Features Overview

### 🎯 **Core SIP Simulation**
- **Multi-fund Portfolio Simulation** - Add multiple mutual funds with custom SIP amounts
- **Historical Performance Analysis** - Simulate SIP investments over custom date ranges
- **Benchmark Comparison** - Compare portfolio performance against Nifty 50 index
- **Interactive Charts** with zoom, pan, and toggle capabilities
- **Real-time Fund Search** with debounced API calls

### 📊 **Risk Analysis Dashboard** ⭐ *NEW*
- **Comprehensive Risk Metrics**:
  - Annual Volatility (Standard Deviation)
  - Sharpe Ratio (Risk-adjusted returns)
  - Sortino Ratio (Downside risk-adjusted)
  - Maximum Drawdown analysis
  - Beta vs Nifty 50
  - Value at Risk (VaR) at 95% confidence
  - Win Rate (Positive months percentage)
- **Portfolio vs Benchmark Risk Comparison**
- **Individual Fund Risk Analysis**
- **Color-coded Risk Levels** (Low/Medium/High)

### 🎯 **Goal-Based Investment Planning** ⭐ *NEW*
- **Retirement Planning Calculator**
  - Inflation-adjusted corpus calculation
  - Post-retirement income planning
  - Years after retirement consideration
- **Child Education Planning**
  - Future education cost estimation
  - Age-based timeline planning
- **Custom Goal Planning**
  - Flexible target amount and timeline
- **SIP Requirement Calculator**
  - Regular SIP vs Step-up SIP comparison
  - Asset allocation recommendations
  - Risk level assessment

### 📈 **Step-up SIP Calculator** ⭐ *NEW*
- **Annual SIP Increase Simulation** (5-25% configurable)
- **Step-up vs Regular SIP Comparison**
- **Wealth Creation Advantage Analysis**
- **Fund-wise Step-up Performance**
- **Dynamic SIP Amount Tracking**

### ⚖️ **Fund Comparison Tool** ⭐ *NEW*
- **Side-by-side Fund Analysis**
- **Category-wise Classification**
- **Risk Level Assessment**
- **Expected Return Ranges**
- **Portfolio Insights**:
  - Diversification Score (1-10)
  - Average Risk Level
  - Expected Portfolio Return
- **Interactive Comparison Table**

### 🌙 **Dark Theme Support** ⭐ *NEW*
- **Toggle between Light/Dark modes**
- **Persistent theme preference**
- **Smooth theme transitions**
- **CSS Variables for consistent theming**

### 📱 **Enhanced User Experience**
- **Tabbed Navigation** - Easy switching between features
- **Progressive Loading** with step-by-step indicators
- **Button Loading States** with spinners
- **Responsive Design** for all device sizes
- **Performance Optimizations**:
  - Thread-safe NAV data caching
  - Parallel processing with ThreadPoolExecutor
  - Reduced API timeouts
  - GPU-accelerated animations

### 📊 **Advanced Chart Features**
- **Magnify/Zoom Functionality**:
  - Mouse wheel zooming
  - Pinch-to-zoom for mobile
  - Zoom controls (In/Out/Reset)
  - Pan mode toggle
- **Chart Type Toggle**:
  - Individual fund performance
  - Portfolio vs Nifty 50 cumulative
- **Interactive Tooltips** with detailed metrics
- **Smooth Animations** and transitions

## 🛠️ Technology Stack

### Backend (Python/Flask)
- **Flask** - Web framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations for risk metrics
- **Requests** - API calls for fund data
- **Threading** - Parallel processing
- **CORS** - Cross-origin resource sharing

### Frontend (Vanilla JavaScript)
- **Chart.js** - Interactive charts with zoom plugin
- **Hammer.js** - Touch gesture support
- **CSS Variables** - Theme system
- **Modern ES6+** - Classes, async/await, modules
- **Responsive CSS Grid/Flexbox**

### External APIs
- **AMFI (Association of Mutual Funds in India)** - Fund data
- **Alternative fund APIs** for enhanced data coverage

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SIPSimulator
```

2. **Install Python dependencies**
```bash
pip install flask flask-cors pandas numpy requests
```

3. **Start the backend server**
```bash
python backend/app.py
```

4. **Open the frontend**
```bash
# Open frontend/index.html in your browser
# Or serve it using a local server:
python -m http.server 8000
# Then visit: http://localhost:8000/frontend/
```

## 📖 Usage Guide

### 1. **SIP Simulation**
1. Set your investment date range
2. Search and add mutual funds
3. Configure SIP amounts for each fund
4. Click "Simulate SIP" to see results
5. Toggle between individual and cumulative charts
6. Use zoom controls for detailed analysis

### 2. **Risk Analysis**
1. Select funds in the SIP Simulator tab
2. Navigate to "Risk Analysis" tab
3. Click "Analyze Portfolio Risk"
4. Review comprehensive risk metrics
5. Compare with benchmark performance

### 3. **Goal Planning**
1. Go to "Goal Planning" tab
2. Select goal type (Retirement/Education/Custom)
3. Fill in relevant details
4. Click "Calculate SIP Requirement"
5. Review SIP recommendations and asset allocation

### 4. **Step-up SIP**
1. Select funds in SIP Simulator
2. Navigate to "Step-up SIP" tab
3. Set annual increase percentage
4. Click "Simulate Step-up SIP"
5. Compare with regular SIP performance

### 5. **Fund Comparison**
1. Add multiple funds in SIP Simulator
2. Go to "Fund Comparison" tab
3. Review side-by-side analysis
4. Check portfolio insights and recommendations

## 🔧 API Endpoints

### Core Endpoints
- `GET /api/search-funds?q={query}` - Search mutual funds
- `POST /api/simulate` - Simulate SIP investments
- `POST /api/benchmark` - Compare with Nifty 50
- `POST /api/cumulative-performance` - Portfolio vs benchmark

### New Feature Endpoints
- `POST /api/risk-analysis` - Comprehensive risk metrics
- `POST /api/goal-planning` - Goal-based SIP calculation
- `POST /api/step-up-sip` - Step-up SIP simulation

## 📊 Risk Metrics Explained

### **Sharpe Ratio**
Measures risk-adjusted returns. Higher is better.
- **> 1.0**: Excellent
- **0.5-1.0**: Good
- **< 0.5**: Poor

### **Sortino Ratio**
Like Sharpe ratio but only considers downside volatility.

### **Maximum Drawdown**
Largest peak-to-trough decline. Lower is better.
- **< 10%**: Low risk
- **10-20%**: Medium risk
- **> 20%**: High risk

### **Beta**
Sensitivity to market movements vs Nifty 50.
- **< 1**: Less volatile than market
- **= 1**: Same as market
- **> 1**: More volatile than market

### **Value at Risk (VaR)**
Potential loss at 95% confidence level.

## 🎨 Customization

### Theme Customization
Modify CSS variables in `frontend/style.css`:
```css
:root {
    --primary-color: #667eea;
    --success-color: #48bb78;
    --danger-color: #e53e3e;
    /* ... more variables */
}
```

### Adding New Features
1. Add backend endpoint in `backend/app.py`
2. Create frontend UI in `frontend/index.html`
3. Add JavaScript functionality in `frontend/script.js`
4. Style with CSS in `frontend/style.css`

## 🔒 Security & Performance

### Security Features
- **Input validation** on all API endpoints
- **Error handling** with graceful fallbacks
- **CORS configuration** for secure cross-origin requests

### Performance Optimizations
- **Caching**: Thread-safe NAV data caching (1-hour expiration)
- **Parallel Processing**: ThreadPoolExecutor for concurrent API calls
- **Debounced Search**: Reduced API calls during typing
- **Optimized Timeouts**: Faster response times
- **GPU Acceleration**: Smooth animations and transitions

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check if port 5000 is available
lsof -i :5000
# Kill any existing process
pkill -f "python.*app.py"
```

**CORS errors:**
- Ensure Flask-CORS is installed
- Check that frontend is accessing correct backend URL

**Chart not loading:**
- Verify Chart.js and plugins are loaded
- Check browser console for JavaScript errors

**API timeouts:**
- Increase timeout values in backend configuration
- Check internet connection for external API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AMFI** for mutual fund data
- **Chart.js** for excellent charting capabilities
- **Font Awesome** for beautiful icons
- **Open source community** for inspiration and tools

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for Indian investors to make informed SIP decisions** 