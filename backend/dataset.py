import pandas as pd
import numpy as np
import os
import random

def load_and_preprocess_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ncr_ride_bookings.csv')
    
    if not os.path.exists(csv_path):
        print(f"WARNING: {csv_path} not found. Generating mock India data fulfilling the schema...")
        n_samples = 1000
        df = pd.DataFrame({
            'Date': ['2024-01-01'] * n_samples,
            'Time': [f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}" for _ in range(n_samples)],
            'Pickup Location': random.choices(['Ahmedabad', 'Mumbai', 'Delhi', 'Bangalore'], k=n_samples),
            'Vehicle Type': random.choices(['Auto', 'Mini', 'Prime', 'Bike'], k=n_samples),
            'Avg VTAT': [random.uniform(5, 45) for _ in range(n_samples)],
            'Booking Value': [random.uniform(50, 800) for _ in range(n_samples)],
        })
    else:
        df = pd.read_csv(csv_path)

    # 1. Base Fare
    if 'Booking Value' in df.columns:
        df['Base_Fare'] = df['Booking Value'].fillna(150.0)
    else:
        df['Base_Fare'] = 150.0
        
    # 2. Time extraction
    if 'Time' in df.columns:
        try:
            df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.hour
            df['Hour'] = df['Hour'].fillna(pd.to_datetime(df['Time'], errors='coerce').dt.hour).fillna(12)
        except:
            df['Hour'] = 12
    else:
        df['Hour'] = 12

    def map_time(h):
        if pd.isna(h): return 'Afternoon'
        h = int(h)
        if 5 <= h < 12: return 'Morning'
        elif 12 <= h < 17: return 'Afternoon'
        elif 17 <= h < 21: return 'Evening'
        else: return 'Night'
    
    df['Time_of_Booking'] = df['Hour'].apply(map_time)

    # 3. Simulate Demand (Booking Counts grouping proxy)
    df['Demand'] = np.random.randint(20, 150, size=len(df)) 
    
    # 4. Simulate Drivers via Vehicle Type
    def simulate_drivers(v_type):
        v = str(v_type).lower()
        if 'bike' in v or 'auto' in v: return random.randint(30, 80)
        return random.randint(10, 40)
        
    df['Drivers'] = df['Vehicle Type'].apply(simulate_drivers) if 'Vehicle Type' in df.columns else 20
    
    df['Demand_Supply_Ratio'] = df['Demand'] / (df['Drivers'] + 1)
    
    # Bridge to old naming conventions
    df['Number_of_Riders'] = df['Demand']
    df['Number_of_Drivers'] = df['Drivers']
    df['Location_Category'] = df['Pickup Location'] if 'Pickup Location' in df.columns else 'Urban'
    df['Traffic_VTAT'] = df['Avg VTAT'] if 'Avg VTAT' in df.columns else 15.0

    return df
