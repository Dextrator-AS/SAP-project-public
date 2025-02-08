import pandas as pd

# Replace 'your_file.json' with the path to your JSON file
file_path = 'heart.json'

# Load the JSON file into a DataFrame
try:
    df = pd.read_json(file_path)
    print("JSON file successfully loaded!")
except ValueError as e:
    print(f"Error loading JSON file: {e}")
    df = None

if df is not None:
    # Ensure the 'timestamp' column is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create a new column to identify weekends and workdays
    df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5  # True for Saturday (5) and Sunday (6), False otherwise
    
    # Filtered time
    time_filtered_df = df[(df['timestamp'].dt.hour >= 6) | (df['timestamp'].dt.hour < 0)]
    print("\nStatistics for filtered time")
    if not time_filtered_df.empty:
        print("Mean heart rate:", time_filtered_df['bpm'].mean())
        print("Median heart rate:", time_filtered_df['bpm'].median())
        print("Lowest heart rate:", time_filtered_df['bpm'].min())
        print("Highest heart rate:", time_filtered_df['bpm'].max())
    else:
        print("No data available for filtered time.")

    # Filtering data for a specific time range (13:00 to 08:00)
    print("\nFiltering data for specific time range...")
    time_filtered_df = df[(df['timestamp'].dt.hour >= 7) & (df['timestamp'].dt.hour < 0)]
    print("Filtered DataFrame:")
    print(time_filtered_df)
else:
    print("DataFrame could not be loaded.")
