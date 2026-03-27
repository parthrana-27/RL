
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from environment import RideEnv
from rl_agent import QLearningAgent
import os

def generate():
    env = RideEnv()
    agent = QLearningAgent(env)
    
    # Define the output folder (project root)
    out = os.path.join(os.path.dirname(__file__), '..', 'results')
    if not os.path.exists(out):
        os.makedirs(out)
    
    # 1. Generate Q_table.csv
    q_rows = []
    for (state_str, action), val in agent.Q.items():
        q_rows.append({"State": state_str, "Action": action, "Q_Value": val})
    q_df = pd.DataFrame(q_rows)
    q_df.to_csv(os.path.join(out, "Q_table.csv"), index=False)
    print("Saved Q_table.csv")
    
    # 2. Q_Values_Scatter_Plot.png
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(q_df)), q_df["Q_Value"], alpha=0.5, color='purple')
    plt.title("Distribution of Learned Q-Values")
    plt.xlabel("State-Action Index")
    plt.ylabel("Q-Value")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(out, "Q_Values_Scatter_Plot.png"))
    plt.close()
    print("Saved Q_Values_Scatter_Plot.png")
    
    # 3. Learning Curve.png (start training from scratch for the report)
    print("Resetting scratchpad for fresh report training...")
    agent.Q = {} # Clear memory for this report but don't delete the saved file on disk yet
    
    print("Running fresh training run (300 episodes) for metrics...")
    metrics = agent.train(episodes=300)
    plt.figure(figsize=(12, 6), dpi=100)
    plt.plot(metrics["rewards"], color='green', linewidth=1.5, alpha=0.9)
    plt.title("AI Performance Convergence (NCR Dataset)", fontsize=14, fontweight='bold')
    plt.xlabel("Training Episode", fontsize=10)
    plt.ylabel("Total Episode Reward ($)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(out, "Learning Curve.png"))
    plt.close()
    print("Saved Learning Curve.png")
    
    # 4. Optimal Path Table.csv & Optimal_Path.png
    state = env.reset()
    done = False
    path_rows = []
    step = 0
    while not done:
        action = max(agent.actions, key=lambda a: agent.get_q(state, a))
        next_state, reward, done, info = env.step(action)
        path_rows.append({
            "Step": step,
            "State (Ratio,Time,Traffic)": str(state),
            "Optimal Multiplier": action,
            "Environment Reward": round(reward, 2),
            "Hour": info["hour"]
        })
        state = next_state
        step += 1
        
    path_df = pd.DataFrame(path_rows)
    path_df.to_csv(os.path.join(out, "Optimal Path Table.csv"), index=False)
    print("Saved Optimal Path Table.csv")
    
    # Line chart of multipliers over 24h
    plt.figure(figsize=(12, 6))
    plt.plot(path_df["Step"], path_df["Optimal Multiplier"], marker='o', color='red', label="Chosen Multiplier")
    plt.axhline(y=1.0, color='black', linestyle='--', label="Static Base")
    plt.title("Optimal Pricing Trajectory (24-Hour Cycle)")
    plt.xlabel("Step (Dataset Row)")
    plt.ylabel("Multiplier (Surge Factor)")
    plt.grid(True, alpha=0.2)
    plt.legend()
    plt.savefig(os.path.join(out, "Optimal_Path.png"))
    plt.close()
    print("Saved Optimal_Path.png")

if __name__ == "__main__":
    generate()
