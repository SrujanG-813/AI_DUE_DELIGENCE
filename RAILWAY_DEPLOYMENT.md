# Railway Deployment Guide

This guide will help you deploy the AI Due Diligence Engine to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **API Key**: Get either an OpenAI or Mistral AI API key
   - OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Mistral AI: [console.mistral.ai](https://console.mistral.ai/)

## Deployment Steps

### 1. Connect Your Repository

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository containing this code
5. Railway will automatically detect the project

### 2. Configure Environment Variables

In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add your API key (choose one):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   OR
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

### 3. Deploy

Railway will automatically:
- Install Python dependencies from `requirements.txt`
- Install Node.js dependencies and build the frontend
- Start the FastAPI server on the assigned port
- Serve both API and frontend from the same domain

The deployment process typically takes 3-5 minutes.

## Configuration Files

The following files are configured for Railway deployment:

- `railway.toml` - Railway-specific configuration
- `nixpacks.toml` - Build configuration for Nixpacks
- `Procfile` - Alternative process definition
- Updated `api_server.py` - Serves frontend and handles Railway port

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | One of these | OpenAI API key for GPT-4 and embeddings |
| `MISTRAL_API_KEY` | One of these | Mistral AI API key (uses HuggingFace embeddings) |
| `PORT` | Auto-set | Railway automatically sets this |

## Accessing Your Application

After deployment:
1. Railway will provide a public URL (e.g., `https://your-app.railway.app`)
2. The frontend will be available at the root URL
3. API documentation will be at `/docs`
4. Health check endpoint at `/api/health`

## Troubleshooting

### Build Issues

If the build fails:
1. Check the build logs in Railway dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify Node.js version compatibility

### Runtime Issues

If the app crashes:
1. Check the deployment logs
2. Verify your API key is set correctly
3. Check the health endpoint: `https://your-app.railway.app/api/health`

### API Key Issues

If you get "No AI provider configured" errors:
1. Verify the environment variable name matches exactly
2. Ensure the API key is valid and has sufficient credits
3. Check the Railway Variables tab for typos

## Cost Considerations

- **Railway**: Free tier includes 500 hours/month, then $5/month
- **OpenAI**: Pay-per-use, typically $0.01-0.10 per analysis
- **Mistral AI**: Pay-per-use, generally cheaper than OpenAI

## Security Notes

- Never commit API keys to your repository
- Use Railway's environment variables for all secrets
- The app includes CORS configuration for web access
- All API endpoints are public (add authentication if needed)

## Scaling

For production use, consider:
- Adding authentication and user management
- Implementing rate limiting
- Adding monitoring and logging
- Using a managed vector database
- Caching analysis results

## Support

If you encounter issues:
1. Check Railway's documentation: [docs.railway.app](https://docs.railway.app)
2. Review the application logs in Railway dashboard
3. Test locally first to isolate deployment vs. code issues