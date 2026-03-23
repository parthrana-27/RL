import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import os

# Load Data
data_path = 'dynamic_pricing.csv'
if not os.path.exists(data_path):
    print(f"Error: Could not find {data_path}")
    exit(1)

df = pd.read_csv(data_path)

# -------------------------------------------------------------
# Environment Preprocessing & MDP Formulation
# -------------------------------------------------------------
print("Preprocessing data and defining MDP states...")

# Calculate Demand-Supply Ratio
df['Demand_Supply_Ratio'] = df['Number_of_Riders'] / df['Number_of_Drivers']

# Bin the Demand_Supply_Ratio into discrete states
bins = [0, 1, 2, 3, np.inf]
labels = ['Low', 'Medium', 'High', 'Very High']
df['Demand_State'] = pd.cut(df['Demand_Supply_Ratio'], bins=bins, labels=labels)

# Combine Demand_State and Time_of_Booking to form state
# Example states: High_Night, Low_Afternoon, etc.
df['State'] = df['Demand_State'].astype(str) + "_" + df['Time_of_Booking']

# Define possible actions (Price Multipliers)
actions = [0.8, 1.0, 1.2, 1.5, 2.0]
n_actions = len(actions)

# Extract unique states
unique_states = df['State'].unique()
n_states = len(unique_states)
state_to_idx = {state: idx for idx, state in enumerate(unique_states)}

print(f"Total Unique States: {n_states}")
print(f"Defined Actions (Multipliers): {actions}")

# -------------------------------------------------------------
# Q-Learning Initialization
# -------------------------------------------------------------
Q_table = np.zeros((n_states, n_actions))

# Q-Learning hyperparameters
learning_rate = 0.1
discount_factor = 0.95
max_exploration_rate = 1.0
min_exploration_rate = 0.01
exploration_decay_rate = 0.001
exploration_rate = max_exploration_rate

# Simulated Environment Step Function
def env_step(state_info, action_idx):
    multiplier = actions[action_idx]
    
    # Calculate simulated acceptance probability
    # Higher price multiplier reduces chance of acceptance, especially if demand relative to supply is low
    ds_ratio = state_info['Demand_Supply_Ratio']
    
    base_acceptance = 0.8
    # If demand is high (ds_ratio high), riders tolerate higher prices
    # We penalize acceptance probability when multiplier > 1.0 and ds_ratio is low
    price_penalty = (multiplier - 1.0) * (2.0 / (ds_ratio + 0.1)) 
    prob_acceptance = max(0.1, min(0.99, base_acceptance - price_penalty))
    
    accepted = np.random.rand() < prob_acceptance
    
    if accepted:
        # Reward is the expected revenue
        reward = state_info['Historical_Cost_of_Ride'] * multiplier
    else:
        # Penalty for driver waiting / lost customer
        reward = -10
        
    return reward

# -------------------------------------------------------------
# Training Loop
# -------------------------------------------------------------
num_episodes = 5000
steps_per_episode = 5
rewards_all_episodes = []

print(f"Starting Q-Learning training for {num_episodes} episodes...")

for episode in range(num_episodes):
    # Sample a random initial state from the dataset to start an episode
    sample_idx = random.randint(0, len(df)-1)
    state_info = df.iloc[sample_idx]
    state_idx = state_to_idx[state_info['State']]
    
    rewards_current_episode = 0
    
    for step in range(steps_per_episode):
        # Exploration-exploitation trade-off (Epsilon-Greedy policy)
        exploration_rate_threshold = random.uniform(0, 1)
        if exploration_rate_threshold > exploration_rate:
            # Exploit: choose best action
            action_idx = np.argmax(Q_table[state_idx, :]) 
        else:
            # Explore: choose random action
            action_idx = random.randint(0, n_actions-1)
            
        # Take action and observe reward
        reward = env_step(state_info, action_idx)
        
        # Next state 
        # For simplicity, we assume the agent encounters a new random ride request
        next_sample_idx = random.randint(0, len(df)-1)
        next_state_info = df.iloc[next_sample_idx]
        next_state_idx = state_to_idx[next_state_info['State']]
        
        # Update Q-table (Bellman Equation)
        best_next_action = np.max(Q_table[next_state_idx, :])
        Q_table[state_idx, action_idx] = Q_table[state_idx, action_idx] * (1 - learning_rate) + \
            learning_rate * (reward + discount_factor * best_next_action)
            
        state_idx = next_state_idx
        state_info = next_state_info
        rewards_current_episode += reward
        
    # Exploration rate decay
    exploration_rate = min_exploration_rate + \
        (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate*episode)
        
    rewards_all_episodes.append(rewards_current_episode)
    
    if (episode + 1) % 1000 == 0:
        avg_reward = np.mean(rewards_all_episodes[-1000:])
        print(f"Episode {episode + 1}/{num_episodes} | Epsilon: {exploration_rate:.3f} | Avg Reward (last 1000): {avg_reward:.2f}")

print("Training finished.")

# -------------------------------------------------------------
# Evaluate and Save Results
# -------------------------------------------------------------
# Save Q-Table to DataFrame for inspection
q_df = pd.DataFrame(Q_table, columns=[f"Price_Multiplier_{a}" for a in actions], index=unique_states)
print("\nLearned Q-Table (Partial):")
print(q_df.head(10))
q_df.to_csv('q_table_results.csv')
print("\n=> Saved Q-Table to q_table_results.csv")

# Plot moving average of rewards
plt.figure(figsize=(10, 6))
moving_avg = np.convolve(rewards_all_episodes, np.ones(100)/100, mode='valid')
plt.plot(moving_avg, label='100-Episode Moving Average')
plt.title('Q-Learning Rewards over Episodes')
plt.xlabel('Episodes')
plt.ylabel('Average Reward')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('learning_curve.png')
print("=> Saved learning curve plot to learning_curve.png")

# Analyze optimal policy
optimal_actions = [actions[np.argmax(Q_table[i, :])] for i in range(n_states)]
policy_df = pd.DataFrame({
    'State': unique_states,
    'Optimal_Price_Multiplier': optimal_actions
})
print("\nOptimal Policy derived from Q-Table:")
print(policy_df.sort_values(by='State').head(16))
policy_df.to_csv('optimal_pricing_policy.csv', index=False)
print("=> Saved optimal policy to optimal_pricing_policy.csv")
