import os
import time
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def fetch_monthly_temperatures(lat, lon):
    """
    Fetches 12-month historical monthly average temperatures (in °C)
    from Open-Meteo's Archive API for the year 2023.
    """
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&monthly=temperature_2m_mean"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            monthly_means = data.get('monthly', {}).get('temperature_2m_mean', [])
            if len(monthly_means) == 12:
                # Round temperatures to 1 decimal place
                return [round(t, 1) if t is not None else None for t in monthly_means]
    except Exception as e:
        print(f"  Weather API error: {e}")
    return [None] * 12

def main():
    input_filename = 'world-cities-with-continents.csv'
    output_filename = 'world_cities_with_monthly_weather.csv'
    
    if not os.path.exists(input_filename):
        print(f"Error: Could not find '{input_filename}' in this folder.")
        return

    # If a previous run was interrupted, resume from it. Otherwise, load the original.
    if os.path.exists(output_filename):
        print(f"Resuming progress from existing file: {output_filename}")
        df = pd.read_csv(output_filename)
    else:
        print(f"Loading original file: {input_filename}")
        df = pd.read_csv(input_filename)

    # Initialize monthly columns if they don't exist yet
    months = ['Jan_Temp_C', 'Feb_Temp_C', 'Mar_Temp_C', 'Apr_Temp_C', 'May_Temp_C', 'Jun_Temp_C',
              'Jul_Temp_C', 'Aug_Temp_C', 'Sep_Temp_C', 'Oct_Temp_C', 'Nov_Temp_C', 'Dec_Temp_C']
    for month in months:
        if month not in df.columns:
            df[month] = None

    # Initialize Geocoder
    geolocator = Nominatim(user_agent="world_cities_monthly_weather_fetcher")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.2) # Avoid hitting OSM rate limits

    # Cache to remember already processed coordinates/weather in this session
    location_cache = {}
    
    print("Starting weather data collection. Press Ctrl+C at any time to safely stop and save.")
    
    saved_counter = 0

    try:
        for index, row in df.iterrows():
            # Check if this row already has data from a prior run
            if pd.notna(row['Jan_Temp_C']):
                continue

            city_query = f"{row['city']}, {row['country']}"
            
            if city_query not in location_cache:
                print(f"Processing ({index + 1}/{len(df)}): {city_query}")
                try:
                    location = geocode(city_query)
                    if location:
                        lat, lon = location.latitude, location.longitude
                        temps = fetch_monthly_temperatures(lat, lon)
                        location_cache[city_query] = temps
                    else:
                        location_cache[city_query] = [None] * 12
                except Exception:
                    location_cache[city_query] = [None] * 12
            
            # Apply temperatures from cache to dataframe
            temps = location_cache[city_query]
            for m_idx, month_col in enumerate(months):
                df.at[index, month_col] = temps[m_idx]

            saved_counter += 1
            # Periodically save backup to disk every 20 unique rows so you don't lose data
            if saved_counter % 20 == 0:
                df.to_csv(output_filename, index=False)
                print(f"  [Progress Saved automatically to {output_filename}]")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving current progress...")
    finally:
        df.to_csv(output_filename, index=False)
        print(f"Successfully saved to: {output_filename}")

if __name__ == "__main__":
    main()
