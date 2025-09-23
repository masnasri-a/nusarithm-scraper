# 🔒 HTTPS Mixed Content Fix - Complete Solution

## 🚨 Problem Summary

The application was experiencing **Mixed Content errors** because:
- Frontend served over HTTPS (`https://scraper.nusarithm.id`)  
- Backend requests made to HTTP endpoints (`http://192.168.8.187:6777`)
- Browsers block HTTP requests from HTTPS pages for security

**Error**: `Mixed Content: The page at 'https://scraper.nusarithm.id/dashboard' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://192.168.8.187:6777/train/'. This request has been blocked.`

---

## ✅ Solutions Implemented

### 1. **Next.js Configuration Update**
**File**: `frontend/next.config.js`
- **Before**: Hardcoded HTTP backend URL (`http://192.168.8.187:6777`)
- **After**: Environment-aware URL resolution

```javascript
async rewrites() {
  const isDev = process.env.NODE_ENV === 'development';
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 
                    (isDev ? 'http://localhost:6777' : 'https://scraper.nusarithm.id/api');
  
  return [
    {
      source: '/api/backend/:path*',
      destination: `${backendUrl}/:path*`,
    },
  ]
}
```

### 2. **Environment Configuration**

**Created**: `frontend/.env.production`
```bash
NEXT_PUBLIC_BACKEND_URL=https://scraper.nusarithm.id/api
```

**Created**: `frontend/.env.local` (for development)
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:6777
```

**Updated**: `.env.template` and `.env.production`
- Added frontend URL configuration
- Production defaults to HTTPS backend

### 3. **Docker Compose Production Update**
**File**: `docker-compose.prod.yml`
- **Before**: `NEXT_PUBLIC_API_URL=http://localhost:6777`
- **After**: `NEXT_PUBLIC_BACKEND_URL=https://scraper.nusarithm.id/api`

### 4. **Nginx Production Configuration**
**File**: `docker/nginx.prod.conf`
- **Added**: HTTPS redirect (HTTP → HTTPS)
- **Updated**: SSL configuration for production
- **Added**: Development config (`nginx.dev.conf`) for local testing

---

## 🌐 URL Structure

| Environment | Frontend | Backend API | Nginx Proxy |
|-------------|----------|-------------|-------------|
| **Development** | http://localhost:3677 | http://localhost:6777 | http://localhost:7777 |
| **Production** | https://scraper.nusarithm.id | https://scraper.nusarithm.id/api | N/A (direct HTTPS) |

---

## 🔧 Configuration Logic

### Automatic Environment Detection
1. **Development**: `NODE_ENV=development` → Use HTTP localhost URLs
2. **Production**: `NODE_ENV=production` → Use HTTPS domain URLs
3. **Override**: Set `NEXT_PUBLIC_BACKEND_URL` to force specific URL

### Request Flow
```mermaid
graph TD
    A[Frontend HTTPS] --> B[/api/backend/*]
    B --> C[Next.js Rewrite]
    C --> D{Environment?}
    D -->|Dev| E[http://localhost:6777]
    D -->|Prod| F[https://scraper.nusarithm.id/api]
    F --> G[Nginx HTTPS]
    G --> H[Backend Container]
```

---

## 🚀 Deployment Instructions

### Development
```bash
# Local development (HTTP)
docker-compose up -d
# Access: http://localhost:7777
```

### Production
```bash
# Production deployment (HTTPS)
chmod +x deploy_production.sh
./deploy_production.sh

# Or manually:
docker-compose -f docker-compose.prod.yml up -d
# Access: https://scraper.nusarithm.id
```

---

## 🔍 Verification Steps

### 1. Check Environment Variables
```bash
# In frontend container
echo $NEXT_PUBLIC_BACKEND_URL

# Should show:
# Development: http://localhost:6777
# Production: https://scraper.nusarithm.id/api
```

### 2. Test API Endpoints
```bash
# Development
curl http://localhost:6777/health

# Production  
curl https://scraper.nusarithm.id/api/health
```

### 3. Browser Network Tab
- All requests should be HTTPS in production
- No "Mixed Content" errors in console
- Check request URLs in Network tab

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

**Issue**: Still getting HTTP requests in production
**Solution**: Clear browser cache, check `NEXT_PUBLIC_BACKEND_URL` environment variable

**Issue**: CORS errors  
**Solution**: Update `CORS_ORIGINS` in backend `.env` to include HTTPS domain

**Issue**: SSL certificate errors
**Solution**: Ensure SSL certificates are properly mounted in nginx container

**Issue**: 502 Bad Gateway
**Solution**: Check if backend container is running and accessible on port 6777

### Debug Commands
```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs scraper-api  
docker-compose -f docker-compose.prod.yml logs nginx

# Test internal connectivity
docker exec -it scraper-frontend curl http://scraper-api:6777/health
```

---

## 📁 Files Modified

### Configuration Files
- ✅ `frontend/next.config.js` - Environment-aware URL rewriting
- ✅ `frontend/.env.production` - Production environment
- ✅ `frontend/.env.local` - Development environment  
- ✅ `docker-compose.prod.yml` - Production container config
- ✅ `.env.template` - Updated template with frontend URLs
- ✅ `.env.production` - Production environment template

### Infrastructure Files  
- ✅ `docker/nginx.prod.conf` - HTTPS nginx configuration
- ✅ `docker/nginx.dev.conf` - Development nginx configuration
- ✅ `deploy_production.sh` - Production deployment script

---

## 🎯 Result

✅ **No more Mixed Content errors**  
✅ **Proper HTTPS communication in production**  
✅ **Seamless development experience with HTTP**  
✅ **Environment-aware configuration**  
✅ **Production-ready deployment scripts**

The application now automatically detects the environment and uses appropriate protocols:
- **Development**: HTTP for local testing
- **Production**: HTTPS for security and compatibility

This ensures compatibility with modern browsers' security requirements while maintaining a smooth development workflow.