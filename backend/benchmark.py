"""
Benchmark script for RideSurge RL
Follows RL.ipynb logic: trains agent, then evaluates RL vs Static pricing.
"""
import pandas as pd
from environment import RideEnv, demand_adjustment
from rl_agent import QLearningAgent

print("Initializing Environment and Agent...")
env = RideEnv()
agent = QLearningAgent(env)

print("Starting training (500 episodes)...")
metrics = agent.train(episodes=500)
print(f"Training complete. Q-table entries: {len(agent.Q)}")

# --- EVALUATION (from RL.ipynb cell 15) ---
print("\nEvaluating RL agent...")
rl_result = agent.evaluate(use_rl=True)

print("Evaluating Static pricing...")
static_result = agent.evaluate(use_rl=False)

print(f"\n===== RESULTS =====")
print(f"RL Revenue: {rl_result}")
print(f"Static Revenue: {static_result}")
print(f"Revenue Increase: {((rl_result - static_result) / abs(static_result)) * 100:.2f}%")

# --- DETAILED TRAJECTORY (from RL.ipynb cells 16-17) ---
print("\nGenerating detailed trajectory for benchmark CSV...")
prices = []
demands = []
utilization_data = []

state = env.reset()
done = False

while not done:
    action = max(env.ACTIONS, key=lambda a: agent.get_q(state, a))
    row = env.df.iloc[env.t]

    demand = row["demand"]
    drivers = row["drivers"]

    adjusted = demand_adjustment(demand, action)
    if action > 2.0:
        adjusted *= 0.7
    rides = min(adjusted, drivers)
    util = rides / (drivers + 1)

    prices.append(action)
    demands.append(demand)
    utilization_data.append(util)

    next_state, _, done, info = env.step(action)
    state = next_state

trajectory_df = pd.DataFrame({
    "hour": list(env.df["hour"])[:-1],
    "demand": demands,
    "price_multiplier": prices,
    "utilization": utilization_data,
})
trajectory_df.to_csv("../data/benchmark_results.csv", index=False)

print("\nDetailed trajectory saved to: data/benchmark_results.csv")
print("Benchmark complete.")
