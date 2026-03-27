"""
Q-Learning Agent for Ride Sharing Dynamic Pricing
Follows the exact logic from RL.ipynb (cells 12-13)
Uses a dictionary-based Q-table with tuple states.
"""
import numpy as np
import json
import os
from environment import RideEnv


class QLearningAgent:
    def __init__(self, env: RideEnv):
        self.env = env
        self.actions = env.ACTIONS  # [1.0, 1.2, 1.5, 2.0, 2.5]

        # Q-table as a dictionary: Q[(state, action)] = value
        self.Q = {}

        # Hyperparameters (from RL.ipynb cell 12)
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

        self.model_path = "q_table.json"

        # Try to load existing Q-table
        if os.path.exists(self.model_path):
            self._load_q_table()

    def get_q(self, state, action):
        """Get Q-value for a (state, action) pair (from RL.ipynb cell 12)"""
        return self.Q.get((str(state), action), 0)

    def choose_action(self, state, exploit_only=False):
        """
        Epsilon-greedy action selection (from RL.ipynb cell 12)
        If exploit_only, always pick the best action.
        """
        if not exploit_only and np.random.rand() < self.epsilon:
            return float(np.random.choice(self.actions))
        return max(self.actions, key=lambda a: self.get_q(state, a))

    def update_q(self, state, action, reward, next_state):
        """Q-learning update rule (from RL.ipynb cell 12)"""
        old_q = self.get_q(state, action)

        if next_state is not None:
            next_max = max([self.get_q(next_state, a) for a in self.actions])
        else:
            next_max = 0

        self.Q[(str(state), action)] = old_q + self.alpha * (
            reward + self.gamma * next_max - old_q
        )

    def train(self, episodes=500):
        """
        Training loop (from RL.ipynb cell 13)
        Each episode = one full sequential pass through the dataset.
        """
        rewards_history = []

        print(f"[RL Agent] Starting training: {episodes} episodes, dataset size: {len(self.env.df)} steps")

        for ep in range(episodes):
            state = self.env.reset()
            total_reward = 0
            done = False

            while not done:
                action = self.choose_action(state)
                next_state, reward, done, info = self.env.step(action)
                self.update_q(state, action, reward, next_state)
                state = next_state
                total_reward += reward

            rewards_history.append(round(total_reward, 2))

            if (ep + 1) % 50 == 0 or ep == 0:
                print(f"  Episode {ep+1}/{episodes} | Total Reward: {total_reward:.0f}")

        self._save_q_table()
        print(f"[RL Agent] Training complete. Q-table entries: {len(self.Q)}")

        return {"rewards": rewards_history}

    def evaluate(self, use_rl=True):
        """
        Evaluation (from RL.ipynb cell 15)
        Returns total revenue for one pass through the dataset.
        """
        state = self.env.reset()
        total_revenue = 0
        done = False

        while not done:
            if use_rl:
                action = max(self.actions, key=lambda a: self.get_q(state, a))
            else:
                action = 1.0  # Static pricing

            next_state, reward, done, info = self.env.step(action)
            total_revenue += reward
            state = next_state

        return total_revenue

    def predict_multiplier(self, state):
        """Predict the best multiplier for a given state tuple, with nearest-neighbor fallback for unseen UI states"""
        state_str = str(state)
        has_exact = any((state_str, a) in self.Q for a in self.actions)

        # Fallback to closest known ratio if the specific slider ratio was never seen in training
        if not has_exact and len(self.Q) > 0:
            target_ratio, t, tr = state
            best_diff = float('inf')
            best_state_str = state_str
            
            for (known_state_str, _) in self.Q.keys():
                try:
                    s = eval(known_state_str)
                    if len(s) == 3 and s[1] == t and s[2] == tr:
                        diff = abs(s[0] - target_ratio)
                        if diff < best_diff:
                            best_diff = diff
                            best_state_str = known_state_str
                except Exception:
                    continue
            
            action = max(self.actions, key=lambda a: self.Q.get((best_state_str, a), 0))
            q_vals = {str(a): self.Q.get((best_state_str, a), 0) for a in self.actions}
            return action, q_vals

        action = max(self.actions, key=lambda a: self.get_q(state, a))
        q_vals = {str(a): self.get_q(state, a) for a in self.actions}
        return action, q_vals

    def reset_table(self):
        """Reset the Q-table"""
        self.Q = {}
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
        print("[RL Agent] Q-table reset.")

    def _save_q_table(self):
        """Save Q-table to JSON file"""
        serializable = {}
        for (state_str, action), value in self.Q.items():
            key = f"{state_str}|{action}"
            serializable[key] = value
        with open(self.model_path, 'w') as f:
            json.dump(serializable, f)
        print(f"[RL Agent] Q-table saved to {self.model_path}")

    def _load_q_table(self):
        """Load Q-table from JSON file"""
        try:
            with open(self.model_path, 'r') as f:
                data = json.load(f)
            self.Q = {}
            for key, value in data.items():
                parts = key.rsplit('|', 1)
                state_str = parts[0]
                action = float(parts[1])
                self.Q[(state_str, action)] = value
            print(f"[RL Agent] Loaded Q-table with {len(self.Q)} entries from {self.model_path}")
        except Exception as e:
            print(f"[RL Agent] Failed to load Q-table: {e}. Starting fresh.")
            self.Q = {}
