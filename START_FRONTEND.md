# 🚀 How to Start the Frontend

## Quick Start Options

### Option 1: Docker Compose (Easiest)
```bash
# Start both frontend and backend
docker-compose up

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Option 2: Manual Setup

#### Step 1: Start the Backend
```bash
# Terminal 1 - Backend
cd /Users/macos/Documents/GitHub/Contest
source venv/bin/activate
python backend/main.py
```

#### Step 2: Start the Frontend
```bash
# Terminal 2 - Frontend
cd /Users/macos/Documents/GitHub/Contest
./start_frontend.sh
```

### Option 3: Individual Services

#### Backend Only
```bash
cd /Users/macos/Documents/GitHub/Contest
source venv/bin/activate
pip install fastapi uvicorn python-multipart
python backend/main.py
```

#### Frontend Only
```bash
cd /Users/macos/Documents/GitHub/Contest/frontend
npm install
npm run dev
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🧪 Test the Setup

### Test Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test airports endpoint  
curl http://localhost:8000/api/airports

# Test search endpoint
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"origin":"LAX","destination":"JFK","date":"2025-12-15","passengers":1}'
```

### Test Frontend
1. Open http://localhost:3000
2. Fill in the search form
3. Click "Search Flights"
4. Verify results appear

## 🔧 Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change port in `backend/main.py`
- **Import errors**: Ensure virtual environment is activated
- **Missing dependencies**: Run `pip install -r backend/requirements.txt`

### Frontend Issues  
- **Port 3000 in use**: Change port in `frontend/vite.config.js`
- **Node.js not found**: Install Node.js from https://nodejs.org/
- **npm install fails**: Clear cache with `npm cache clean --force`

### Connection Issues
- **CORS errors**: Check backend CORS settings
- **API not responding**: Verify backend is running on port 8000
- **Network errors**: Check firewall settings

## 📱 Features to Test

### Search Form
- ✅ Airport selection dropdowns
- ✅ Date picker
- ✅ Passenger count
- ✅ Swap airports button

### Results Display
- ✅ Flight cards with pricing
- ✅ CPP calculation
- ✅ Loading states
- ✅ Error handling

### Responsive Design
- ✅ Mobile layout
- ✅ Tablet layout  
- ✅ Desktop layout

## 🎯 Expected Behavior

1. **Search Form**: Clean, intuitive interface
2. **Loading**: Spinner while searching
3. **Results**: Flight cards with pricing data
4. **Errors**: Clear error messages
5. **Responsive**: Works on all screen sizes

## 🚀 Production Deployment

### Build for Production
```bash
# Build frontend
cd frontend
npm run build

# Build backend
docker build -t aa-scraper-backend ./backend
```

### Environment Variables
```bash
# Backend
export PYTHONPATH=/app
export API_HOST=0.0.0.0
export API_PORT=8000

# Frontend
export VITE_API_URL=http://localhost:8000
```

## 🎉 Success!

If everything is working, you should see:
- ✅ Beautiful, modern web interface
- ✅ Working search functionality
- ✅ Real-time flight data
- ✅ Responsive design
- ✅ Professional UI/UX

**Happy searching! ✈️**
