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

    # Print the DataFrame to verify
    print("Updated DataFrame with 'is_weekend' column:")
    print(df)

    # Statistics for all data
    print("\nStatistics for all data")
    print("Mean heart rate:", df['bpm'].mean())
    print("Median heart rate:", df['bpm'].median())
    print("Lowest heart rate:", df['bpm'].min())
    print("Highest heart rate:", df['bpm'].max())

    # Statistics for weekends
    weekend_data = df[df['is_weekend']]
    print("\nStatistics for weekends")
    if not weekend_data.empty:
        print("Mean heart rate:", weekend_data['bpm'].mean())
        print("Median heart rate:", weekend_data['bpm'].median())
        print("Lowest heart rate:", weekend_data['bpm'].min())
        print("Highest heart rate:", weekend_data['bpm'].max())
    else:
        print("No data available for weekends.")

    # Statistics for workdays
    workday_data = df[~df['is_weekend']]
    print("\nStatistics for workdays")
    if not workday_data.empty:
        print("Mean heart rate:", workday_data['bpm'].mean())
        print("Median heart rate:", workday_data['bpm'].median())
        print("Lowest heart rate:", workday_data['bpm'].min())
        print("Highest heart rate:", workday_data['bpm'].max())
    else:
        print("No data available for workdays.")

    # Filtered time
    time_filtered_df = df[(df['timestamp'].dt.hour >= 13) | (df['timestamp'].dt.hour < 8)]
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
    time_filtered_df = df[(df['timestamp'].dt.hour >= 13) | (df['timestamp'].dt.hour < 8)]
    print("Filtered DataFrame:")
    print(time_filtered_df)
else:
    print("DataFrame could not be loaded.")



    time_filtered_df = df[(df['timestamp'].dt.hour >= 8) & (df['timestamp'].dt.hour < 13)]
    print("\nStatistics for filtered time")
    if not time_filtered_df.empty:
        print("Mean heart rate:", time_filtered_df['bpm'].mean())
        print("Median heart rate:", time_filtered_df['bpm'].median())
        print("Lowest heart rate:", time_filtered_df['bpm'].min())
        print("Highest heart rate:", time_filtered_df['bpm'].max())
    else:
        print("No data available for filtered time.")
