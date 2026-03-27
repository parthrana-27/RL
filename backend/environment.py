"""
RideEnv - Ride Sharing Environment for Offline RL
Follows the exact logic from RL.ipynb
"""
from dataset import load_and_preprocess_data


def demand_adjustment(base_demand, multiplier):
    """
    Demand Elasticity Model (from RL.ipynb cell 10)
    elasticity = -0.8 means demand drops as price increases
    """
    elasticity = -0.8
    return base_demand * (multiplier ** elasticity)


class RideEnv:
    """
    Data-driven environment (from RL.ipynb cell 11)
    - Sequential row-by-row transitions through the preprocessed dataset
    - No random sampling, no stochastic transitions
    """

    # Action space: 5 discrete multipliers (from RL.ipynb cell 9)
    ACTIONS = [1.0, 1.2, 1.5, 2.0, 2.5]

    def __init__(self):
        self.df, self.base_price = load_and_preprocess_data()
        self.t = 0

    def reset(self):
        """Reset environment to the beginning of the dataset"""
        self.t = 0
        return self.get_state()

    def get_state(self):
        """
        Extract state tuple from current row (from RL.ipynb cell 11)
        State = (rounded ratio, time_slot, traffic)
        """
        row = self.df.iloc[self.t]
        return (float(format(float(row["ratio"]), '.1f')), int(row["time_slot"]), int(row["traffic"]))

    def step(self, action):
        """
        Execute one step in the environment (from RL.ipynb cell 11)
        action = the price multiplier (float from ACTIONS)
        Returns: (next_state, reward, done, info)
        """
        row = self.df.iloc[self.t]

        demand = row["demand"]
        drivers = row["drivers"]

        # Apply pricing effect via demand elasticity
        adjusted_demand = demand_adjustment(demand, action)

        # Passenger cancellation behavior (from RL.ipynb cell 11)
        if action > 2.0:
            adjusted_demand *= 0.7

        rides = min(adjusted_demand, drivers)

        # Revenue from real data
        revenue = rides * self.base_price * action

        wait_time = max(0, adjusted_demand - drivers)

        # Cancellation penalty (from dataset approx)
        cancel_rate = 0.1 if action > 2.0 else 0.05
        cancel_penalty = cancel_rate * demand

        reward = revenue - 0.5 * wait_time - 2 * cancel_penalty

        self.t += 1
        done = self.t >= len(self.df) - 1

        next_state = self.get_state() if not done else None

        info = {
            "demand": float(demand),
            "drivers": float(drivers),
            "adjusted_demand": float(adjusted_demand),
            "rides": float(rides),
            "revenue": float(revenue),
            "wait_time": float(wait_time),
            "cancel_penalty": float(cancel_penalty),
            "reward": float(reward),
            "multiplier": float(action),
            "hour": int(row["hour"]),
            "time_slot": int(row["time_slot"]),
            "traffic": int(row["traffic"]),
            "ratio": float(row["ratio"]),
        }

        return next_state, reward, done, info
