# 🚀 SIP Simulator - Render Deployment

Quick deployment guide for hosting the SIP Simulator on Render.com

## 📋 Prerequisites

- GitHub account
- Render.com account (free tier available)

## 🚀 Quick Deploy to Render

### Method 1: One-Click Deploy (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Method 2: Manual Deployment

1. **Fork/Clone this repository to your GitHub account**

2. **Create a new Web Service on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - **Name**: `sip-simulator`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/app_production.py`
   - **Plan**: Free (or paid for better performance)

4. **Set Environment Variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here
   LOG_LEVEL=INFO
   CORS_ORIGINS=*
   ```

5. **Deploy**: Click "Create Web Service"

## 🌐 Access Your Application

After deployment, your app will be available at:
- `https://your-app-name.onrender.com`

## 📊 Features Available

- ✅ Full SIP Simulation
- ✅ Risk Analysis
- ✅ Goal Planning
- ✅ Step-up SIP Calculator
- ✅ Fund Comparison
- ✅ Dark Theme Support
- ✅ Responsive Design

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed origins | `*` |
| `PORT` | Server port | Auto-assigned |

## 🚨 Troubleshooting

### Common Issues

1. **Build fails**: Check requirements.txt for compatibility
2. **App doesn't start**: Verify start command
3. **404 errors**: Check file paths and routing
4. **Slow response**: Upgrade to paid plan for better performance

### Logs

View application logs in the Render dashboard:
- Go to your service → "Logs" tab

## 📈 Performance Optimization

### Free Tier Limitations

- Sleeps after 15 minutes of inactivity
- Limited CPU and memory
- Shared infrastructure

### Upgrading

For production use, consider upgrading to a paid plan:
- Faster startup times
- More memory and CPU
- No sleep mode
- Custom domains

## 🔒 Security

The application includes:
- ✅ Security headers
- ✅ Rate limiting
- ✅ CORS protection
- ✅ Input validation
- ✅ Error handling

## 📞 Support

If you encounter issues:

1. Check Render logs first
2. Verify environment variables
3. Test locally with production settings
4. Contact support via GitHub issues

## 📝 Notes

- The app uses mock data for demonstration
- Real fund data would require additional API integrations
- Free tier has usage limitations

---

**Happy Investing! 📈** 