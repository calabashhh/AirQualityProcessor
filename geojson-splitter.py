import json
import os
from datetime import datetime

def create_monthly_geojson(input_file, output_dir='output'):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the input GeoJSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Get a list of all monthly columns
    monthly_columns = [key for key in data['features'][0]['properties'].keys() 
                      if any(month in key for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])]
    
    # Base columns to keep in each file
    base_columns = [
        "left", "bottom", "right", "top", "GEOJOIN",
        "ChinaAQIPoints_Updated_Name", "ChinaAQIPoints_Updated_address",
        "ChinaAQIPoints_Updated_file_name", "ChinaAQIPoints_Updated_Lat",
        "ChinaAQIPoints_Updated_Long", "ChinaAQIPoints_Updated_Current AQI"
    ]
    
    # Create a new GeoJSON file for each month
    for month_column in monthly_columns:
        # Create new GeoJSON structure
        new_geojson = {
            "type": "FeatureCollection",
            "name": f"ChinaAQI_{month_column}",
            "crs": data['crs'],
            "features": []
        }
        
        # Process each feature
        for feature in data['features']:
            new_feature = {
                "type": "Feature",
                "properties": {},
                "geometry": feature['geometry']
            }
            
            # Add base columns
            for col in base_columns:
                new_feature['properties'][col] = feature['properties'].get(col, None)
            
            # Add monthly average value
            monthly_value = feature['properties'].get(month_column)
            new_feature['properties']["Monthly_average"] = 0 if monthly_value is None else monthly_value
            
            new_geojson['features'].append(new_feature)
        
        # Create filename
        # Extract year and month from column name (assuming format like "ChinaAQIPoints_Updated_Jan2014")
        month_year = month_column.split('_')[-1]  # Gets "Jan2014"
        filename = f"{month_year}_average.geojson"
        
        # Save the file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w') as f:
            json.dump(new_geojson, f, indent=2)

def main():
    # Assuming the input file is in the same directory
    input_file = "china_aqi.geojson"
    
    try:
        create_monthly_geojson(input_file)
        print("Successfully created monthly GeoJSON files in the 'output' directory.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
