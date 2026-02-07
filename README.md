# SynTeCX Hub - ML House Price Prediction Platform

A production-ready, startup-grade machine learning platform for house price prediction with explainable AI, real-time analytics, and comprehensive dashboard interface.

## Features

- **Multiple ML Models**: Linear Regression, Random Forest, XGBoost with automated model selection
- **Explainable AI**: Feature importance, confidence scores, and human-readable explanations
- **Real-time Analytics**: Interactive dashboards, what-if analysis, and trend visualization
- **Production Ready**: Scalable architecture, comprehensive testing, and deployment-ready
- **Modern UI**: Dark/light mode, responsive design, and intuitive user experience

## Tech Stack

### Backend
- **FastAPI**: High-performance REST API with automatic documentation
- **Python**: scikit-learn, XGBoost, pandas, numpy
- **PostgreSQL**: Metadata storage and model versioning
- **Redis**: Caching and session management

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern styling utilities
- **Recharts**: Data visualization components

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (optional, for containerized deployment)

### Development Setup

1. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

3. **Full Stack with Docker:**
```bash
docker-compose up --build
```

## Project Structure

```
syntecx_hub/
├── backend/                    # FastAPI backend service
├── frontend/                   # Next.js React frontend
├── data/                       # Data management
├── docs/                       # Documentation
├── docker-compose.yml          # Container orchestration
└── README.md                   # This file
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Key Endpoints

- `POST /api/v1/predictions` - Get house price prediction with explanation
- `POST /api/v1/predictions/what-if` - Real-time what-if analysis
- `GET /api/v1/analytics/feature-importance` - Feature importance data
- `POST /api/v1/models/train` - Train new model version

## Development Workflow

1. **Branch Strategy**: Feature branches from `main`
2. **Code Quality**: Pre-commit hooks, type hints, comprehensive testing
3. **CI/CD**: Automated testing and deployment pipelines
4. **Documentation**: Inline docs and API documentation

## Production Deployment

See `docs/deployment.md` for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - SynTeCX Technologies 2024