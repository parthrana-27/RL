import gym
from gym import spaces
import numpy as np
import random
from dataset import load_and_preprocess_data

class RideSharingEnv(gym.Env):
    def __init__(self):
        super(RideSharingEnv, self).__init__()
        self.df = load_and_preprocess_data()
        
        # We model the state as a sequence of factors:
        # Demand-supply (0-3), Time of day (0-3), Traffic level (0-2)
        self.n_demand_states = 4
        self.n_time_states = 4
        self.n_traffic_states = 3
        
        self.n_states = self.n_demand_states * self.n_time_states * self.n_traffic_states
        
        # Actions: 6 discrete multipliers
        self.n_actions = 6
        self.multipliers = [0.8, 1.0, 1.2, 1.5, 1.8, 2.0]
        
        self.action_space = spaces.Discrete(self.n_actions)
        self.observation_space = spaces.Discrete(self.n_states)
        
        self.current_step = 0
        self.max_steps = 100 # Episode length = 100 steps (simulated hours/periods)
        self.state_info = None
        self.reset()
        
    def _extract_state_components(self, row):
        # 1. Demand Supply Ratio
        ds_ratio = row['Demand_Supply_Ratio']
        if ds_ratio < 1.0: ds_level = 0
        elif ds_ratio < 2.0: ds_level = 1
        elif ds_ratio < 3.0: ds_level = 2
        else: ds_level = 3
            
        # 2. Time of day
        t_str = str(row['Time_of_Booking']).lower()
        if 'morning' in t_str: time_val = 0
        elif 'afternoon' in t_str: time_val = 1
        elif 'evening' in t_str: time_val = 2
        else: time_val = 3
            
        # 3. Traffic Level via VTAT (Vehicle Turn Around Time)
        vtat = float(row.get('Traffic_VTAT', 15.0))
        # High VTAT means high traffic/long delays
        if vtat < 12.0: traffic_val = 0     # Low Traffic
        elif vtat < 25.0: traffic_val = 1   # Medium Traffic
        else: traffic_val = 2               # High Traffic
            
        return ds_level, time_val, traffic_val

    def _get_state_index(self, ds_level, time_val, traffic_val):
        return ds_level * (self.n_time_states * self.n_traffic_states) + time_val * self.n_traffic_states + traffic_val

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        sample_idx = random.randint(0, len(self.df) - 1)
        self.state_info = self.df.iloc[sample_idx]
        
        ds, t, tr = self._extract_state_components(self.state_info)
        return self._get_state_index(ds, t, tr), {}
        
    def step(self, action_idx):
        multiplier = self.multipliers[action_idx]
        base_fare = self.state_info['Base_Fare']
        ds_ratio = self.state_info['Demand_Supply_Ratio']
        
        base_prob = 0.8
        acceptance_prob = max(0.1, min(0.99, base_prob - (multiplier - 1.0) * (2.0 / (ds_ratio + 0.1))))
        
        accepted = random.random() < acceptance_prob
        
        if accepted:
            reward = base_fare * multiplier
            wait_time = max(0, 300 - ds_ratio * 50) 
        else:
            reward = -50 
            wait_time = 0
            
        self.current_step += 1
        terminated = self.current_step >= self.max_steps
        truncated = False
        
        sample_idx = random.randint(0, len(self.df) - 1)
        self.state_info = self.df.iloc[sample_idx]
        ds, t, tr = self._extract_state_components(self.state_info)
        next_state_idx = self._get_state_index(ds, t, tr)
        
        info = {
            "accepted": accepted,
            "reward": reward,
            "wait_time": wait_time,
            "ds_ratio": {"riders": int(self.state_info['Number_of_Riders']), "drivers": int(self.state_info['Number_of_Drivers'])},
            "multiplier": multiplier,
            "base_fare": base_fare,
            "time_val": t,
            "traffic_val": tr
        }
        
        return next_state_idx, reward, terminated, truncated, info
        
    def render(self):
        pass
