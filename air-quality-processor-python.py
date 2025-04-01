import pandas as pd
import numpy as np
from datetime import datetime
import os

def process_air_quality_data(main_file):
    # Read the main Excel file
    stations_df = pd.read_excel(main_file)
    
    # Generate all month columns from Jan 2014 to Nov 2024
    start_date = pd.to_datetime('2014-01-01')
    end_date = pd.to_datetime('2024-11-30')
    month_range = pd.date_range(start_date, end_date, freq='M')
    month_columns = [d.strftime('%b%Y') for d in month_range]
    
    # Initialize these columns in the dataframe with NaN
    for col in month_columns:
        stations_df[col] = np.nan
    
    # Process each station
    for idx, row in stations_df.iterrows():
        station_name = row['Name']
        filename = f"{row['file_name']}.csv"
        
        print(f"Processing {station_name}...")
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                continue
                
            # Read the station's CSV file
            station_data = pd.read_csv(filename)
            
            # Clean up the pm25 column - convert to numeric, handling errors
            station_data[' pm25'] = pd.to_numeric(station_data[' pm25'].str.strip(), errors='coerce')
            
            # Convert date column to datetime
            station_data['date'] = pd.to_datetime(station_data['date'], format='%Y/%m/%d')
            
            # Drop any rows where pm25 is NaN
            station_data = station_data.dropna(subset=[' pm25'])
            
            # Group by month and calculate average PM2.5
            monthly_avg = station_data.groupby(station_data['date'].dt.strftime('%b%Y'))[' pm25'].mean()
            
            # Update the main dataframe with the monthly averages
            for month, value in monthly_avg.items():
                if month in stations_df.columns:
                    stations_df.at[idx, month] = value
                    
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    # Save the updated dataframe to a new Excel file
    output_file = 'ChinaAQIPoints_Updated.xlsx'
    stations_df.to_excel(output_file, index=False)
    print(f"\nProcessing complete. Results saved to {output_file}")
    
    return stations_df

def main():
    # Specify the main Excel file
    main_file = 'ChinaAQIPoints.xlsx'
    
    try:
        # Process the data
        result_df = process_air_quality_data(main_file)
        
        # Print some basic statistics
        print("\nSummary Statistics:")
        print(f"Total stations processed: {len(result_df)}")
        
        # Calculate completeness of data
        data_columns = [col for col in result_df.columns if col.startswith(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))]
        completeness = result_df[data_columns].notna().sum().sum() / (len(result_df) * len(data_columns)) * 100
        print(f"Data completeness: {completeness:.2f}%")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
