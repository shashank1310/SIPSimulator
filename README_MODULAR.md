# SIP Simulator - Modular Architecture

## 🏗️ Project Structure

The SIP Simulator has been refactored into a clean, modular architecture for better maintainability and scalability.

### Backend Structure

```
backend/
├── app_new.py                 # Main Flask application (streamlined)
├── config.py                  # Configuration settings
├── data/
│   └── fund_data.py          # Fund data and search functionality
├── routes/
│   ├── simulation_routes.py  # SIP simulation endpoints
│   ├── analysis_routes.py    # Risk analysis and goal planning endpoints
│   └── fund_routes.py        # Fund search endpoints
├── services/
│   ├── simulation_service.py # Simulation business logic
│   ├── portfolio_service.py  # Portfolio processing logic
│   ├── risk_service.py       # Risk analysis logic (to be created)
│   └── goal_service.py       # Goal planning logic (to be created)
└── utils/
    ├── calculations.py       # Financial calculations
    └── data_generator.py     # Data generation utilities
```

### Frontend Structure

```
frontend/
├── index.html               # Main HTML file
├── style.css               # Styles
├── script.js               # Legacy monolithic file (for reference)
└── js/
    ├── core/
    │   └── SIPSimulator.js  # Main SIP Simulator class
    ├── modules/
    │   ├── ThemeManager.js  # Theme management
    │   ├── NavigationManager.js # Tab navigation
    │   ├── FundManager.js   # Fund search and management
    │   ├── SimulationManager.js # SIP simulation logic
    │   ├── AnalysisManager.js # Risk analysis and goal planning
    │   ├── ChartManager.js  # Chart creation and management
    │   └── ComparisonManager.js # Fund comparison logic
    └── app.js               # Application initialization
```

## 🚀 Getting Started

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install flask flask-cors pandas numpy scipy requests
   ```

2. **Run the New Modular Backend**
   ```bash
   python app_new.py
   ```

3. **API Endpoints**
   - `POST /api/simulate` - SIP simulation
   - `POST /api/cumulative-performance` - Portfolio vs benchmark
   - `POST /api/benchmark` - Nifty 50 comparison
   - `POST /api/step-up-sip` - Step-up SIP simulation
   - `POST /api/risk-analysis` - Risk metrics
   - `POST /api/goal-planning` - Financial goal planning
   - `GET /api/search-funds` - Fund search
   - `GET /api/funds` - All funds

### Frontend Setup

1. **Serve Frontend**
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```

2. **Access Application**
   Open `http://localhost:8080` in your browser

## 📁 Module Descriptions

### Backend Modules

#### `config.py`
- Configuration constants and settings
- API timeouts, cache durations
- Risk analysis parameters
- Asset allocation templates

#### `data/fund_data.py`
- Comprehensive fund list
- Fund search functionality
- Online fund data augmentation
- Caching mechanisms

#### `routes/`
- **simulation_routes.py**: SIP simulation endpoints
- **analysis_routes.py**: Risk analysis and goal planning
- **fund_routes.py**: Fund search and listing

#### `services/`
- **simulation_service.py**: Core simulation business logic
- **portfolio_service.py**: Portfolio processing with parallel execution
- **risk_service.py**: Risk metrics calculation (to be implemented)
- **goal_service.py**: Goal planning logic (to be implemented)

#### `utils/`
- **calculations.py**: Financial calculations (XIRR, CAGR, risk metrics)
- **data_generator.py**: NAV data generation and SIP simulation

### Frontend Modules

#### `core/SIPSimulator.js`
- Main application class
- Event listeners setup
- Core functionality coordination

#### `modules/ThemeManager.js`
- Light/dark theme switching
- Theme persistence in localStorage
- Theme-related UI updates

#### `modules/NavigationManager.js`
- Tab navigation management
- Goal type form handling
- Content switching logic

#### `modules/FundManager.js`
- Fund search functionality
- Selected funds management
- Fund categorization and risk assessment

## 🔧 Migration Guide

### From Monolithic to Modular

1. **Backend Migration**
   - Replace `app.py` with `app_new.py`
   - Existing functionality is preserved
   - Better error handling and logging
   - Improved performance with parallel processing

2. **Frontend Migration**
   - Update HTML to include modular JavaScript files
   - Replace single `script.js` with multiple modules
   - Maintain backward compatibility

### Key Improvements

1. **Separation of Concerns**
   - Each module has a single responsibility
   - Easier to test and maintain
   - Better code organization

2. **Performance Enhancements**
   - Parallel processing for fund data
   - Optimized caching mechanisms
   - Reduced memory footprint

3. **Scalability**
   - Easy to add new features
   - Modular architecture supports growth
   - Clear interfaces between components

4. **Maintainability**
   - Smaller, focused files
   - Clear dependencies
   - Better error isolation

## 🧪 Testing

### Backend Testing
```bash
# Test individual endpoints
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"funds": [{"fund_name": "Test Fund", "scheme_code": "122639", "sip_amount": 10000}], "start_date": "2023-01-01", "end_date": "2024-01-01"}'
```

### Frontend Testing
- Open browser developer tools
- Check console for any errors
- Test all tabs and functionality
- Verify theme switching works

## 📈 Performance Benefits

1. **Reduced Load Times**
   - Modular loading of JavaScript
   - Smaller initial bundle size
   - Better caching strategies

2. **Improved Responsiveness**
   - Parallel backend processing
   - Non-blocking UI operations
   - Better error handling

3. **Memory Efficiency**
   - Lazy loading of modules
   - Better garbage collection
   - Reduced memory leaks

## 🔮 Future Enhancements

1. **Additional Modules**
   - Portfolio optimization
   - Tax calculation
   - Rebalancing suggestions
   - Performance attribution

2. **Advanced Features**
   - Real-time data integration
   - Machine learning predictions
   - Advanced charting options
   - Export functionality

3. **Technical Improvements**
   - TypeScript migration
   - Unit test coverage
   - API documentation
   - Docker containerization

## 🤝 Contributing

1. Follow the modular structure
2. Add new features as separate modules
3. Maintain backward compatibility
4. Include proper error handling
5. Update documentation

## 📝 Notes

- The original `app.py` and `script.js` files are preserved for reference
- All existing functionality is maintained in the modular version
- The new structure is designed for easy extension and maintenance
- Performance improvements are built-in with the new architecture 