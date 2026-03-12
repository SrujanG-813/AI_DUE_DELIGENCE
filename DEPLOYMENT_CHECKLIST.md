# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

### Configuration Files
- [x] `railway.toml` - Railway configuration
- [x] `nixpacks.toml` - Build configuration  
- [x] `Procfile` - Process definition
- [x] `railway.json` - Template configuration
- [x] Updated `api_server.py` for production
- [x] Updated `vite.config.ts` for build
- [x] Updated `.env.example` with both API options

### Code Changes
- [x] FastAPI serves static files from frontend build
- [x] CORS configured for production (`allow_origins=["*"]`)
- [x] Port configuration from environment variable
- [x] Frontend uses relative API paths (`/api/`)
- [x] Build output directory configured (`dist/`)

### Dependencies
- [x] All Python dependencies in `requirements.txt`
- [x] All Node.js dependencies in `frontend/package.json`
- [x] Added `requests` for health checks

### Documentation
- [x] `RAILWAY_DEPLOYMENT.md` - Detailed deployment guide
- [x] Updated `README.md` with Railway deployment info
- [x] `DEPLOYMENT_CHECKLIST.md` - This checklist

## 🚀 Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect and deploy

3. **Set Environment Variables**
   In Railway dashboard → Variables tab:
   ```
   MISTRAL_API_KEY=your_mistral_key_here
   ```
   OR
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

4. **Verify Deployment**
   - Check build logs for errors
   - Visit your Railway URL
   - Test `/api/health` endpoint
   - Upload a document and run analysis

## 🔍 Post-Deployment Verification

### Health Check
- [ ] Visit `https://your-app.railway.app/api/health`
- [ ] Should return: `{"status": "healthy", "api_key_configured": true, "provider": "..."}`

### Frontend Test
- [ ] Main page loads correctly
- [ ] File upload works
- [ ] Sample documents button works

### API Test
- [ ] Upload a document
- [ ] Analysis completes successfully
- [ ] Results display correctly
- [ ] Risk memo generates

### Performance Check
- [ ] Page loads in < 3 seconds
- [ ] Analysis completes in reasonable time
- [ ] No console errors

## 🐛 Troubleshooting

### Build Fails
1. Check Railway build logs
2. Verify `requirements.txt` and `package.json`
3. Check Node.js/Python version compatibility

### App Crashes
1. Check Railway deployment logs
2. Verify environment variables are set
3. Test health endpoint

### API Errors
1. Verify API key is correct and has credits
2. Check CORS configuration
3. Verify file upload size limits

### Frontend Issues
1. Check if build files exist in `frontend/dist/`
2. Verify static file serving in `api_server.py`
3. Check browser console for errors

## 📊 Monitoring

After deployment, monitor:
- Railway metrics (CPU, memory, requests)
- API usage and costs (OpenAI/Mistral)
- Error rates and response times
- User feedback and usage patterns

## 🔒 Security Notes

- API keys are stored securely in Railway environment variables
- CORS is configured for web access (consider restricting for production)
- No authentication implemented (add if needed for production use)
- File uploads are temporary and cleaned up automatically

## 💰 Cost Estimation

**Railway**: 
- Free tier: 500 hours/month
- Pro: $5/month + usage

**AI APIs**:
- Mistral: ~$0.01-0.05 per analysis
- OpenAI: ~$0.05-0.15 per analysis

**Total**: Expect $10-50/month for moderate usage