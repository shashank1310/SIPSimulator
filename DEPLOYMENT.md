# 🚀 SIP Simulator - Production Deployment Guide

This guide covers various production deployment options for the SIP Simulator application.

## 📋 Prerequisites

- **Linux Server** (Ubuntu 18.04+ recommended)
- **Python 3.8+**
- **Git**
- **Nginx** (for reverse proxy)
- **Redis** (for caching, optional but recommended)
- **SSL Certificate** (for HTTPS, recommended)

## 🔧 Quick Start - Standard Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd SIPSimulator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env

# Set production values:
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
APP_HOST=0.0.0.0
APP_PORT=5000
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### 3. Run in Production Mode

```bash
# Using the production runner
python run_production.py
```

## 🐳 Docker Deployment (Recommended)

### 1. Docker Compose (Easiest)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3

# Stop services
docker-compose down
```

### 2. Manual Docker Build

```bash
# Build image
docker build -t sip-simulator .

# Run container
docker run -d \
  --name sip-simulator \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -v $(pwd)/logs:/app/logs \
  sip-simulator
```

## 🔧 Systemd Service Deployment

### 1. Install as System Service

```bash
# Copy service file
sudo cp sip-simulator.service /etc/systemd/system/

# Edit service file if needed
sudo nano /etc/systemd/system/sip-simulator.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable sip-simulator

# Start service
sudo systemctl start sip-simulator

# Check status
sudo systemctl status sip-simulator
```

### 2. Service Management Commands

```bash
# Start service
sudo systemctl start sip-simulator

# Stop service
sudo systemctl stop sip-simulator

# Restart service
sudo systemctl restart sip-simulator

# View logs
sudo journalctl -u sip-simulator -f

# Disable auto-start
sudo systemctl disable sip-simulator
```

## 🌐 Nginx Configuration

### 1. Install Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. Configure Nginx

```bash
# Copy configuration
sudo cp nginx.conf /etc/nginx/sites-available/sip-simulator

# Create symlink
sudo ln -s /etc/nginx/sites-available/sip-simulator /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🔒 SSL/HTTPS Setup

### 1. Using Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Using Custom Certificate

```bash
# Place your certificates
sudo cp your-cert.crt /etc/ssl/certs/
sudo cp your-key.key /etc/ssl/private/

# Update Nginx configuration
# Uncomment HTTPS section in nginx.conf
```

## 📊 Monitoring and Logging

### 1. Application Logs

```bash
# View application logs
tail -f logs/app.log

# View Gunicorn logs
tail -f logs/gunicorn_access.log
tail -f logs/gunicorn_error.log

# View system logs
sudo journalctl -u sip-simulator -f
```

### 2. Nginx Logs

```bash
# Access logs
tail -f /var/log/nginx/sip_simulator_access.log

# Error logs
tail -f /var/log/nginx/sip_simulator_error.log
```

### 3. Health Monitoring

```bash
# Check application health
curl http://localhost:5000/health

# Check via Nginx
curl http://yourdomain.com/health
```

## ⚡ Performance Optimization

### 1. Gunicorn Tuning

Edit `gunicorn.conf.py`:

```python
# Adjust workers based on your server
workers = multiprocessing.cpu_count() * 2 + 1

# For CPU-intensive tasks
worker_class = "sync"

# For I/O intensive tasks
# worker_class = "gevent"
# worker_connections = 1000
```

### 2. Caching

```bash
# Install Redis
sudo apt install redis-server

# Configure in .env
REDIS_URL=redis://localhost:6379/0

# Enable caching in config
CACHE_ENABLED=True
```

### 3. Database Optimization (Future)

```bash
# For PostgreSQL (if needed)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb sipsimuator
```

## 🔧 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode | `development` | Yes |
| `SECRET_KEY` | Flask secret key | - | Yes |
| `APP_HOST` | Server host | `0.0.0.0` | No |
| `APP_PORT` | Server port | `5000` | No |
| `REDIS_URL` | Redis connection | - | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed origins | `*` | No |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `True` | No |

## 🛠️ Deployment Checklist

### Pre-deployment

- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS origins
- [ ] Set up SSL certificates
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Create backups

### Security

- [ ] Disable debug mode
- [ ] Enable security headers
- [ ] Configure rate limiting
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Monitor logs

### Performance

- [ ] Configure caching
- [ ] Optimize worker count
- [ ] Set up CDN (if needed)
- [ ] Database optimization
- [ ] Monitor resources

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /path/to/app
   chmod +x run_production.py
   ```

3. **Service won't start**
   ```bash
   sudo journalctl -u sip-simulator -n 50
   ```

4. **Nginx 502 Bad Gateway**
   ```bash
   # Check if backend is running
   curl http://localhost:5000/health
   
   # Check Nginx error logs
   sudo tail -f /var/log/nginx/error.log
   ```

### Performance Issues

1. **High memory usage**
   - Reduce worker count
   - Enable request limits
   - Monitor for memory leaks

2. **Slow response times**
   - Enable caching
   - Optimize database queries
   - Use CDN for static files

3. **High CPU usage**
   - Scale horizontally
   - Optimize algorithms
   - Use async workers

## 📞 Support

For deployment issues:

1. Check logs first
2. Review configuration
3. Test individual components
4. Check system resources
5. Consult documentation

## 🔄 Updates and Maintenance

```bash
# Update application
git pull origin main
pip install -r requirements.txt

# Restart services
sudo systemctl restart sip-simulator
sudo systemctl restart nginx

# Or with Docker
docker-compose pull
docker-compose up -d
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Multiple app instances
docker-compose up -d --scale backend=3

# Load balancer configuration
# Add upstream servers in nginx.conf
```

### Vertical Scaling

- Increase server resources
- Adjust worker counts
- Optimize database
- Use faster storage

---

**🎉 Congratulations!** Your SIP Simulator is now production-ready! 