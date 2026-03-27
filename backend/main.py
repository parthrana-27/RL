"""
FastAPI Backend for RideSurge RL
All logic follows RL.ipynb exactly.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from environment import RideEnv
from rl_agent import QLearningAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize environment and agent
env = RideEnv()
agent = QLearningAgent(env)


class TrainRequest(BaseModel):
    episodes: int = 500


class SimulateRequest(BaseModel):
    steps: int = 1
    riders: int = None
    drivers: int = None
    time_val: int = None
    traffic_val: int = None


@app.post("/train")
def train_model(req: TrainRequest):
    """Train the Q-learning agent and return metrics + benchmark"""
    metrics = agent.train(episodes=req.episodes)

    # Evaluate RL vs Static (from RL.ipynb cell 15)
    rl_result = agent.evaluate(use_rl=True)
    static_result = agent.evaluate(use_rl=False)

    benchmark = {
        "rl_revenue": round(float(rl_result), 2),
        "static_revenue": round(float(static_result), 2),
        "rl_utilization": round(float(rl_result) / max(1, float(static_result)) * 100, 1),
        "static_utilization": 100.0,
    }
    return {"message": "Training Complete", "metrics": metrics, "benchmark": benchmark}


@app.post("/reset")
def reset_table():
    """Reset the Q-table and the environment"""
    agent.reset_table()
    env.reset()
    return {"message": "Environment and Q-Table reset successfully"}


@app.post("/simulate")
def simulate(req: SimulateRequest):
    """Run a simulation and return pricing history"""
    history = []

    # Custom simulation parameters provided
    if req.riders is not None and req.drivers is not None:
        ds_ratio = req.riders / (req.drivers + 1)
        t = req.time_val if req.time_val is not None else 1
        tr = req.traffic_val if req.traffic_val is not None else 1

        state = (float(format(ds_ratio, '.1f')), t, tr)
        action, q_vals = agent.predict_multiplier(state)

        # Calculate expected results for this single state point (manual sliders)
        from environment import demand_adjustment
        adj_demand = demand_adjustment(req.riders, action)
        if action > 2.0:
            adj_demand *= 0.7  # cancellation factor
        rides = min(adj_demand, req.drivers)
        
        # Revenue and Wait logic influenced by Time/Traffic
        traffic_multi = {0: 1.0, 1: 1.25, 2: 1.6}.get(tr, 1.0)   # Traffic scales wait time
        time_multi = {0: 1.1, 1: 1.0, 2: 1.15}.get(t, 1.0)      # Peak times scale revenue baseline
        
        revenue = rides * env.base_price * action * time_multi
        
        # Static baseline for this single scenario
        st_adj = demand_adjustment(req.riders, 1.0)
        st_rides = min(st_adj, req.drivers)
        st_revenue = st_rides * env.base_price * 1.0 * time_multi

        wait_time = (max(0, adj_demand - req.drivers) + (50 * tr)) * traffic_multi

        slot_names = ["Morning", "Afternoon", "Evening"]
        t_str = slot_names[t] if 0 <= t < len(slot_names) else "Unknown"
        traffic_names = ["Low", "Medium", "High"]
        tr_str = traffic_names[tr] if 0 <= tr < len(traffic_names) else "Unknown"

        return {
            "simulation": {
                "state": str(state),
                "recommended_multiplier": action,
                "q_values": q_vals,
                "revenue": float(format(revenue, '.2f')),
                "static_revenue": float(format(st_revenue, '.2f')),
                "rides": float(format(rides, '.1f')),
                "wait_time": float(format(wait_time, '.1f')),
                "utilization": float(format((rides / max(1, req.drivers)) * 100, '.1f')),
                "explanation": f"Custom scenario during {t_str} with {tr_str} traffic."
            }
        }

    # Free-running simulation using internal dataset
    state = env.reset()
    rl_revenue = 0.0
    static_revenue = 0.0
    wait_time_sum = 0.0
    total_rides = 0.0
    done = False
    step_count = 0

    while not done and step_count < req.steps:
        # RL agent action
        action = agent.choose_action(state, exploit_only=True)

        # Static baseline (multiplier 1.0)
        row = env.df.iloc[env.t]
        from environment import demand_adjustment
        st_demand = row["demand"]
        st_drivers = row["drivers"]
        st_adjusted = demand_adjustment(st_demand, 1.0)
        st_rides = min(st_adjusted, st_drivers)
        static_revenue += st_rides * env.base_price * 1.0

        # RL step
        next_state, reward, done, info = env.step(action)

        history.append({
            "step": step_count,
            "multiplier": info["multiplier"],
            "reward": round(info["reward"], 2),
            "wait_time": round(info["wait_time"], 2),
            "time_val": info["time_slot"],
            "traffic_val": info["traffic"],
            "ds_ratio": {"riders": int(info["demand"]), "drivers": int(info["drivers"])},
            "q_values": {str(a): agent.get_q(state, a) for a in agent.actions},
        })

        rl_revenue += info["revenue"]
        wait_time_sum += info["wait_time"]
        total_rides += info["rides"]

        state = next_state
        step_count += 1

        if done:
            state = env.reset()
            done = False  # allow continuing if more steps requested

    return {
        "history": history,
        "summary": {
            "rl_revenue": round(rl_revenue, 2),
            "static_revenue": round(static_revenue, 2),
            "avg_wait_time": round(wait_time_sum / max(1, step_count), 2),
            "utilization": round(total_rides / max(1, step_count), 1),
        }
    }


@app.get("/status")
def status():
    """Return Q-table stats"""
    return {
        "q_table_entries": len(agent.Q),
        "total_actions": len(agent.actions),
        "actions": agent.actions,
        "epsilon": agent.epsilon,
        "alpha": agent.alpha,
        "gamma": agent.gamma,
        "dataset_size": len(env.df),
        "base_price": round(env.base_price, 2),
    }
