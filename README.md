# RideSurge RL

A Reinforcement Learning-powered dynamic pricing model for ride-sharing platforms.

## Development Instructions

1. **Backend Server**:
    Navigate to the `backend/` directory, install requirements, and run the FastAPI server:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
    ```
    
2. **Frontend App**:
    Navigate to the `frontend/` directory, install Node packages, and run the Vite dev server:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3. Open `http://localhost:5173` in your browser.

## Built With
- **Backend:** Python 3.11, FastAPI, OpenAI Gym 0.26, scikit-learn, numpy, pandas
- **Frontend:** React 18, Vite, TypeScript, TailwindCSS, Zustand, Recharts, Framer Motion, Leaflet
- **Data:** Original dataset stored as `dynamic_pricing_dataset.csv` in `data/`

## Innovative Features Included
- "Explain My Price" logic via click on map
- Q-Table Tabular Reinforcement Training directly from the dashboard
- Real-time Epsilon decay progress & dynamic chart visualizing reward climb
- Export 24-hr Simulation history CSV
- Comparison bar charts simulating Static vs RL pricing rules

Enjoy the environment!
