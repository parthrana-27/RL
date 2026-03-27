import pandas as pd
import numpy as np
import os

def load_and_preprocess_data():
    """
    Loads and preprocesses the NCR ride bookings dataset.
    Follows the exact logic from RL.ipynb:
    1. Load raw CSV
    2. Create DateTime, extract hour
    3. Demand = all bookings grouped by hour
    4. Supply = completed rides grouped by hour
    5. Merge demand + supply
    6. Traffic = time-based proxy
    7. State features: ratio, time_slot, traffic
    8. Base price from real data (mean Booking Value)
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ncr_ride_bookings.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please place ncr_ride_bookings.csv in the data/ folder.")

    print("INFO: Loading dataset...")
    df_raw = pd.read_csv(csv_path)

    # --- 2. PREPROCESSING ---
    df_raw["DateTime"] = pd.to_datetime(df_raw["Date"] + " " + df_raw["Time"], errors='coerce')
    df_raw["hour"] = df_raw["DateTime"].dt.hour
    # Fill NaN hours with 12 (noon)
    df_raw["hour"] = df_raw["hour"].fillna(12).astype(int)

    # --- 3. DEMAND (All bookings per hour) ---
    demand_df = df_raw.groupby("hour").size().reset_index(name="demand")

    # --- 4. SUPPLY (Completed rides per hour) ---
    completed_df = df_raw[df_raw["Booking Status"] == "Completed"]
    supply_df = completed_df.groupby("hour").size().reset_index(name="drivers")

    # --- 5. MERGE DEMAND + SUPPLY ---
    df = pd.merge(demand_df, supply_df, on="hour", how="left")
    df.fillna({"drivers": 0}, inplace=True)

    # --- 6. TRAFFIC (Time-based proxy) ---
    def get_traffic(hour):
        if 8 <= hour <= 10 or 18 <= hour <= 21:
            return 2  # High
        elif 11 <= hour <= 17:
            return 1  # Medium
        else:
            return 0  # Low

    df["traffic"] = df["hour"].apply(get_traffic)

    # --- 7. STATE FEATURES ---
    df["ratio"] = df["demand"] / (df["drivers"] + 1)

    def get_time_slot(h):
        if h < 12:
            return 0
        elif h < 18:
            return 1
        else:
            return 2

    df["time_slot"] = df["hour"].apply(get_time_slot)

    # --- 8. BASE PRICE (REAL DATA) ---
    # Use mean of Booking Value from raw data, filling NaN with 150
    booking_vals = df_raw["Booking Value"].dropna()
    if len(booking_vals) > 0:
        base_price = float(booking_vals.mean())
    else:
        base_price = 150.0

    print(f"INFO: Dataset preprocessed. {len(df)} hourly time steps. Base price: {base_price:.2f}")

    return df, base_price
