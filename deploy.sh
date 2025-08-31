#!/bin/bash
# 🚀 SolysAI Deployment Script

echo "🚀 Starting SolysAI Full-Stack Deployment..."
echo "================================================"

# Step 1: Backend Deployment (Railway)
echo "📡 Deploying Backend to Railway..."
cd backend
railway login
railway init
railway up
echo "✅ Backend deployed! Note your Railway URL."

# Step 2: Frontend Deployment (Vercel) 
echo "🌐 Deploying Frontend to Vercel..."
cd ../frontend
vercel login
vercel --prod
echo "✅ Frontend deployed! Note your Vercel URL."

echo "================================================"
echo "🎉 Deployment Complete!"
echo "📋 Next Steps:"
echo "1. Setup MongoDB Atlas database"
echo "2. Add environment variables in Railway & Vercel"
echo "3. Update CORS settings"
echo "4. Test your live application"
echo "================================================"
echo "📚 Full guide: COMPLETE_DEPLOYMENT_GUIDE.md"
