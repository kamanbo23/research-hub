#!/bin/bash

echo "Research Application Deployment Helper"
echo "======================================"
echo ""
echo "This script helps you deploy your application without Docker."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is required but not installed. Please install Git first."
    exit 1
fi

# Check if the repository is committed
if [[ -n $(git status -s) ]]; then
    echo "You have uncommitted changes. Please commit them before continuing."
    read -p "Do you want to commit all changes with a generic message? (y/n): " answer
    if [[ "$answer" == "y" ]]; then
        git add .
        git commit -m "Prepare for deployment"
    else
        echo "Please commit your changes manually and run this script again."
        exit 1
    fi
fi

echo "Where do you want to deploy your application?"
echo "1. Backend to Render, Frontend to Vercel (recommended)"
echo "2. Only Backend to Render (if you want to deploy frontend separately)"
echo "3. Only Frontend to Vercel (if you've already deployed the backend)"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Deploying both backend and frontend..."
        echo ""
        echo "STEP 1: Backend Deployment to Render"
        echo "1. Go to https://render.com and sign up or log in."
        echo "2. Connect your GitHub repository."
        echo "3. Click 'New +' > 'Web Service'."
        echo "4. Select your repository and configure as follows:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:\$PORT"
        echo "   - Set the environment variables as mentioned in the README.md"
        echo ""
        echo "STEP 2: Update the Frontend .env file"
        read -p "Enter your backend's deployed URL (e.g., https://researchapp-api.onrender.com): " backend_url
        echo "REACT_APP_API_URL=$backend_url" > ./frontend/.env
        echo "Frontend .env file updated with backend URL: $backend_url"
        echo ""
        echo "STEP 3: Frontend Deployment to Vercel"
        echo "1. Go to https://vercel.com and sign up or log in."
        echo "2. Click 'Add New' > 'Project'"
        echo "3. Import your repository and configure as follows:"
        echo "   - Framework Preset: Create React App"
        echo "   - Root Directory: frontend"
        echo "   - Build Command: npm run build"
        echo "4. Click 'Deploy'"
        ;;
    2)
        echo "Deploying only the backend..."
        echo "1. Go to https://render.com and sign up or log in."
        echo "2. Connect your GitHub repository."
        echo "3. Click 'New +' > 'Web Service'."
        echo "4. Select your repository and configure as follows:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:\$PORT"
        echo "   - Set the environment variables as mentioned in the README.md"
        ;;
    3)
        echo "Deploying only the frontend..."
        read -p "Enter your backend's deployed URL (e.g., https://researchapp-api.onrender.com): " backend_url
        echo "REACT_APP_API_URL=$backend_url" > ./frontend/.env
        echo "Frontend .env file updated with backend URL: $backend_url"
        echo ""
        echo "Frontend Deployment to Vercel"
        echo "1. Go to https://vercel.com and sign up or log in."
        echo "2. Click 'Add New' > 'Project'"
        echo "3. Import your repository and configure as follows:"
        echo "   - Framework Preset: Create React App"
        echo "   - Root Directory: frontend"
        echo "   - Build Command: npm run build"
        echo "4. Click 'Deploy'"
        ;;
    *)
        echo "Invalid choice. Please run the script again and select a valid option."
        exit 1
        ;;
esac

echo ""
echo "Deployment instructions complete. Follow the steps above to finish deploying your application."
echo "For more detailed instructions, refer to the README.md file." 