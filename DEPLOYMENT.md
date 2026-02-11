# Deployment Guide

## Quick Deploy Options

### Option 1: Coolify (Recommended)

1. **Add New Resource** → Git Repository
2. **Repository:** `https://github.com/Roastcoder/vehicle-valuation-engine`
3. **Build Pack:** Dockerfile
4. **Port:** 8080
5. **Environment Variables:**
   ```
   SUREPASS_API_TOKEN=your_surepass_token
   GEMINI_API_KEY=your_gemini_key
   ```
6. **Deploy**

Your API will be available at: `https://your-app.coolify.io`

### Option 2: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
cd "resale calculaator"
railway login
railway init
railway up

# Add environment variables
railway variables set SUREPASS_API_TOKEN=your_token
railway variables set GEMINI_API_KEY=your_key
```

### Option 3: Render

1. **New Web Service**
2. **Connect Repository:** `Roastcoder/vehicle-valuation-engine`
3. **Environment:** Docker
4. **Port:** 8080
5. **Environment Variables:**
   - `SUREPASS_API_TOKEN`
   - `GEMINI_API_KEY`
6. **Create Web Service**

### Option 4: DigitalOcean App Platform

1. **Create App** → GitHub
2. **Select Repository:** `vehicle-valuation-engine`
3. **Dockerfile:** Auto-detected
4. **HTTP Port:** 8080
5. **Environment Variables:** Add tokens
6. **Deploy**

## Environment Variables Required

```bash
SUREPASS_API_TOKEN=your_surepass_api_token
GEMINI_API_KEY=your_gemini_api_key
```

## Health Check Endpoint

```
GET /health
```

## Test Deployment

```bash
# Replace with your domain
curl https://your-domain.com/health

# Test Gemini endpoint
curl -X POST https://your-domain.com/api/v1/idv/gemini \
  -H "Content-Type: application/json" \
  -d '{"rc_number": "DL08AB1234"}'
```

## Docker Manual Deploy

```bash
# Build
docker build -t vehicle-valuation .

# Run locally
docker run -p 8080:8080 \
  -e SUREPASS_API_TOKEN=your_token \
  -e GEMINI_API_KEY=your_key \
  vehicle-valuation

# Test
curl http://localhost:8080/health
```

## Production Checklist

- ✅ Environment variables configured
- ✅ Port 8080 exposed
- ✅ Health check endpoint working
- ✅ Database auto-creates on startup
- ✅ CORS enabled (if needed for frontend)
- ✅ Rate limiting (optional)
- ✅ Logging configured

## Troubleshooting

**Issue:** Port not accessible
- Check firewall rules
- Verify port 8080 is exposed
- Check container logs

**Issue:** API tokens not working
- Verify environment variables are set
- Check token format (no quotes)
- Test tokens separately

**Issue:** Database errors
- Database auto-creates on first request
- Check write permissions
- Verify disk space
