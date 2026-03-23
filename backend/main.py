from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import random
from environment import RideSharingEnv
from rl_agent import QLearningAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = RideSharingEnv()
agent = QLearningAgent(env)

class TrainRequest(BaseModel):
    episodes: int = 1000

class SimulateRequest(BaseModel):
    steps: int = 1
    riders: int = None
    drivers: int = None
    time_val: int = None
    traffic_val: int = None

@app.post("/train")
def train_model(req: TrainRequest):
    metrics = agent.train(episodes=req.episodes)
    
    # Run a quick 1000-step benchmark post-training
    state, _ = env.reset()
    rl_revenue, static_revenue, rl_accepted, static_accepted = 0, 0, 0, 0
    
    for _ in range(1000):
        action = agent.act(state, exploit_only=True)
        next_state, reward, term, trunc, info = env.step(action)
        
        if random.random() < 0.8:
            static_revenue += info["base_fare"]
            static_accepted += 1
            
        if info["accepted"]:
            rl_revenue += info["base_fare"] * info["multiplier"]
            rl_accepted += 1
            
        state = next_state
        if term or trunc:
            state, _ = env.reset()
            
    benchmark = {
        "rl_utilization": round((rl_accepted / 1000) * 100, 1),
        "static_utilization": round((static_accepted / 1000) * 100, 1),
        "rl_revenue": round(rl_revenue, 2),
        "static_revenue": round(static_revenue, 2)
    }
    return {"message": "Training Complete", "metrics": metrics, "benchmark": benchmark}

@app.post("/reset")
def reset_table():
    agent.reset_table()
    return {"message": "Q-Table Reset successfully"}

@app.post("/simulate")
def simulate(req: SimulateRequest):
    history = []
    
    # Custom simulation parameters provided
    if req.riders is not None and req.drivers is not None:
        ds_ratio = req.riders / (req.drivers + 1)
        ds_level = 0 if ds_ratio < 1.0 else (1 if ds_ratio < 2.0 else (2 if ds_ratio < 3.0 else 3))
        
        t = req.time_val if req.time_val is not None else random.randint(0, 3)
        tr = req.traffic_val if req.traffic_val is not None else random.randint(0, 2)
        
        state_idx = env._get_state_index(ds_level, t, tr)
        action, multiplier, q_vals = agent.predict_multiplier(state_idx)
        
        t_str = ["Morning", "Afternoon", "Evening", "Night"][t]
        return {
            "simulation": {
                "state_idx": state_idx,
                "recommended_multiplier": multiplier,
                "q_values": q_vals,
                "explanation": f"High demand bridging {t_str} + low drivers (India peak hours)" if ds_level > 1 else "Normal baseline volume"
            }
        }
        
    # Free-running simulation using internal dataset
    state, _ = env.reset()
    rl_revenue = 0
    static_revenue = 0
    wait_time_sum = 0
    acceptances = 0
    
    for _ in range(req.steps):
        action = agent.act(state, exploit_only=True)
        # 1.0 multiplier action is idx 1
        static_action = 1
        
        # We need info for calculating static revenue
        curr_info = env.state_info
        static_fare = curr_info['Base_Fare']
        static_prob = max(0.1, min(0.99, 0.8))
        if random.random() < static_prob:
            static_revenue += static_fare
            
        next_state, reward, terminated, truncated, info = env.step(action)
        history.append({
            "step": _,
            "ds_ratio": info["ds_ratio"],
            "multiplier": info["multiplier"],
            "reward": reward,
            "wait_time": info["wait_time"],
            "time_val": info["time_val"],
            "traffic_val": info["traffic_val"],
            "q_values": agent.q_table[state, :].tolist()
        })
        
        if info["accepted"]:
            rl_revenue += info["base_fare"] * info["multiplier"]
            wait_time_sum += info["wait_time"]
            acceptances += 1
            
        state = next_state
        if terminated or truncated:
            state, _ = env.reset()
            
    return {
        "history": history,
        "summary": {
            "rl_revenue": rl_revenue,
            "static_revenue": static_revenue,
            "avg_wait_time": wait_time_sum / max(1, acceptances),
            "utilization": acceptances / req.steps * 100
        }
    }

@app.get("/status")
def status():
    non_zero = np.count_nonzero(agent.q_table)
    total = agent.q_table.size
    return {
        "q_table_sparsity": f"{(total - non_zero) / total * 100:.2f}%",
        "total_states": agent.n_states,
        "n_actions": agent.n_actions,
        "epsilon": agent.epsilon
    }
