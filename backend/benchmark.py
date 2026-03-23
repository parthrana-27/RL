import pandas as pd
import numpy as np
from environment import RideSharingEnv
from rl_agent import QLearningAgent

print("Initializing Environment and Agent...")
env = RideSharingEnv()
agent = QLearningAgent(env)

print("Starting training (2000 episodes)...")
metrics = agent.train(episodes=2000)
print(f"Training complete. Q-Table trained entries: {np.count_nonzero(agent.q_table)}")

print("Running global simulation benchmark (1000 steps)...")
state, _ = env.reset()
rl_revenue = 0
static_revenue = 0
rl_wait_time = 0
static_wait_time = 0
rl_accepted = 0
static_accepted = 0

history = []

for step in range(1000):
    # RL Agent takes action
    action = agent.act(state, exploit_only=True)
    next_state, reward, terminated, truncated, info = env.step(action)
    
    ds_ratio = info['ds_ratio']['riders'] / (info['ds_ratio']['drivers'] + 1)
    
    if info["accepted"]:
        rl_revenue += info["base_fare"] * info["multiplier"]
        rl_wait_time += info["wait_time"]
        rl_accepted += 1
        
    # Simulate Static Pricing (Action 1 is multiplier 1.0)
    # The acceptance probability for 1.0 multiplier is essentially base_prob (0.8) without elasticity penalty
    base_fare = info['base_fare']
    static_prob = max(0.1, min(0.99, 0.8))
    static_accepted_bool = np.random.random() < static_prob
    
    if static_accepted_bool:
        static_revenue += base_fare
        static_wait_time += max(0, 300 - ds_ratio * 50)
        static_accepted += 1

    history.append({
        "step": step,
        "ds_ratio": round(ds_ratio, 2),
        "time_of_day": info["time_val"],
        "traffic_level": info["traffic_val"],
        "rl_multiplier": info["multiplier"],
        "rl_reward": round(reward, 2),
        "rl_wait_time_s": round(info["wait_time"], 2) if info["accepted"] else None,
        "rl_accepted": info["accepted"],
        "static_accepted": static_accepted_bool
    })
    
    state = next_state
    if terminated or truncated:
        state, _ = env.reset()

summary = {
    "rl_total_revenue($)": round(rl_revenue, 2),
    "static_total_revenue($)": round(static_revenue, 2),
    "revenue_increase(%)": round(((rl_revenue - static_revenue) / static_revenue) * 100, 2) if static_revenue > 0 else 0,
    "rl_avg_wait_time(s)": round(rl_wait_time / max(1, rl_accepted), 2),
    "static_avg_wait_time(s)": round(static_wait_time / max(1, static_accepted), 2),
    "rl_driver_utilization(%)": round((rl_accepted / 1000) * 100, 2),
    "static_driver_utilization(%)": round((static_accepted / 1000) * 100, 2)
}

df = pd.DataFrame(history)
df.to_csv("../data/benchmark_results.csv", index=False)

print("\n=== FINAL BENCHMARK SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v}")
print("\nResults detailed trajectory saved to: data/benchmark_results.csv")
