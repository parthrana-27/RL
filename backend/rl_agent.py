import numpy as np
import os
from environment import RideSharingEnv

class QLearningAgent:
    def __init__(self, env):
        self.env = env
        self.n_states = env.n_states
        self.n_actions = env.n_actions
        self.q_table = np.zeros((self.n_states, self.n_actions))
        
        # Learning parameters
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.model_path = "q_table.npy"
        
        if os.path.exists(self.model_path):
            self.q_table = np.load(self.model_path)
            self.epsilon = self.min_epsilon
            
    def act(self, state, exploit_only=False):
        if exploit_only or np.random.rand() > self.epsilon:
            return np.argmax(self.q_table[state, :])
        return self.env.action_space.sample()
        
    def train(self, episodes=1000):
        metrics = {
            "rewards": [],
            "revenues": [],
            "wait_times": []
        }
        self.epsilon = 1.0 # Start exploring
        decay_rate = (1.0 - self.min_epsilon) / episodes
        
        for ep in range(episodes):
            state, _ = self.env.reset()
            ep_reward = 0
            ep_revenue = 0
            ep_wait_time = 0
            acceptances = 0
            
            terminated = False
            truncated = False
            while not (terminated or truncated):
                action = self.act(state)
                next_state, reward, terminated, truncated, info = self.env.step(action)
                
                # Q-learning update
                best_next_action = np.max(self.q_table[next_state, :])
                self.q_table[state, action] = self.q_table[state, action] * (1 - self.alpha) + \
                    self.alpha * (reward + self.gamma * best_next_action)
                    
                state = next_state
                ep_reward += reward
                if info["accepted"]:
                    ep_revenue += info["base_fare"] * info["multiplier"]
                    ep_wait_time += info["wait_time"]
                    acceptances += 1
            
            # Save episode metrics
            metrics["rewards"].append(ep_reward)
            metrics["revenues"].append(ep_revenue)
            metrics["wait_times"].append(ep_wait_time / max(1, acceptances))
            
            self.epsilon = max(self.min_epsilon, self.epsilon - decay_rate)
            
        np.save(self.model_path, self.q_table)
        return metrics

    def predict_multiplier(self, state_idx):
        action = np.argmax(self.q_table[state_idx, :])
        multiplier = self.env.multipliers[action]
        q_vals = self.q_table[state_idx, :].tolist()
        return action, multiplier, q_vals

    def reset_table(self):
        self.q_table = np.zeros((self.n_states, self.n_actions))
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
        self.epsilon = 1.0
