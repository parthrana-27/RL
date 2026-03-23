
---

## 3. Backend – Exact Logic (Python + FastAPI)
- **environment.py**:
  - Class `RideSharingEnv(gym.Env)` with `reset()`, `step(action)`, `render()`
  - State calculation: `demand_supply_ratio = riders / (drivers + 1)`
  - Time_of_day encoded 0-3 (Morning/Afternoon/Evening/Night)
  - Traffic & location from dataset columns
  - Episode length = 100 steps (simulated hours)
- **rl_agent.py**:
  - Tabular Q-Learning (Q-table 4D: state_space × 6 actions)
  - ε-greedy exploration (start ε=1.0, decay to 0.01)
  - Learning rate α=0.1, discount γ=0.95
  - Train endpoint `/train` (1000 episodes, save q_table.npy)
  - Inference endpoint `/predict_multiplier` (returns best action + explanation)
- **dataset.py**:
  - Load Kaggle CSV, create demand-supply imbalance, simulate traffic
  - Pre-compute base_fare from `Historical_Cost_of_Ride`
- **main.py**:
  - FastAPI routes:
    - `POST /simulate` → run N steps, return JSON with pricing history
    - `POST /train` → trigger training + return metrics
    - `GET /status` → current Q-table stats + revenue comparison
  - CORS enabled for frontend

---

## 4. Frontend – UI/UX Requirements (React + TypeScript + Tailwind + Recharts + Leaflet)
**Must be modern, dark-mode, responsive, single-page app**

### 4.1 Dashboard (Home)
- Hero banner: "RideSurge RL – AI that prices rides smarter"
- Live stats cards (real-time):
  - Current Price Multiplier (big animated number)
  - Revenue Today (vs Static)
  - Avg Wait Time (seconds)
  - Driver Utilization %

### 4.2 Live Pricing Map (`LivePricingMap.tsx`)
- Leaflet map (center on "Ahmedabad" or random city)
- Heatmap overlay: color intensity = current price multiplier per zone
- Click any zone → shows state vector + recommended multiplier
- Real-time pulsing markers for active rides & waiting drivers

### 4.3 Training Panel (`TrainingPanel.tsx`)
- Button "Start Training (1000 episodes)"
- Live progress bar + episode counter
- Real-time line chart: Reward, Revenue, Wait Time (update every 50 episodes)
- Epsilon decay curve
- After training: "Q-Table Trained ✓" + download button

### 4.4 Simulation Controls (`Controls.tsx`)
Sliders & inputs:
- Number of Riders (real-time)
- Number of Drivers
- Time of Day (dropdown)
- Traffic Level (slider 0-2)
- "Run Simulation" button → triggers `/simulate` and updates map + charts instantly

### 4.5 Comparison Chart (`ComparisonChart.tsx`)
- Side-by-side Recharts:
  - RL Pricing vs Static Pricing (revenue & wait time)
  - Bar chart: Revenue gain %
  - Line chart: Price multiplier over simulated 24 hours
- Toggle "Show RL vs Static" switch

### 4.6 Footer
- "Built with Q-Learning + FastAPI + React"
- Link to original Kaggle dataset + GitHub repo (placeholder)

**UI Theme:** Dark (bg-zinc-950), accents in neon green (#22c55e) and purple (#a855f7). All animations smooth (Framer Motion).

---

## 5. Exact Tech Stack (NO deviations)
- **Backend**: Python 3.11, FastAPI, uvicorn, pandas, numpy, gym==0.26, scikit-learn
- **Frontend**: React 18 + Vite + TypeScript + TailwindCSS + Recharts + Leaflet + Axios
- **State Management**: Zustand (for live simulation data)
- **No other libraries** (especially no TensorFlow/PyTorch – pure numpy Q-table)

---

## 6. Development & Run Instructions (Must be in README.md)
1. `pip install -r requirements.txt`
2. Place `ncr_ride_bookings.csv` in `/data/`
3. `cd backend && uvicorn main:app --reload`
4. `cd frontend && npm install && npm run dev`
5. Open http://localhost:5173

---

## 7. Bonus Innovative Features (MANDATORY – do NOT skip)
- "Explain My Price" modal: when multiplier changes, shows Q-value breakdown + "Why this price? High demand in Evening + low drivers"
- Export simulation as CSV + video recording button (using canvas capture)
- "Reset Q-Table" button
- Dark/Light theme toggle (auto-detect)

---

**FINAL INSTRUCTION TO ANTIGRAVITY:**  
Generate the **complete project** in ONE response (zip-ready structure) that strictly follows every single point above.  
Use the exact file names, component names, API endpoints, MDP dimensions, action space, reward formula, and Kaggle dataset.  
Make the UI beautiful, interactive, and production-ready.  
This is an **innovative academic + demo assignment** – it must look impressive for a college project or portfolio.

Start generating now. Output the full code in the exact folder structure.