# Approximately_Weather_Temperature_Per_Month_Of_Cities_In_The_World
To add columns for all 12 months with their approximate average monthly temperatures to your `world-cities (1).csv` file, you can use Python with pandas, geopy (to get the coordinates), and the requests library to fetch data from the free Open-Meteo Climate API.
​Since your CSV file likely contains thousands of rows, making individual API requests for every single row will take a long time and might hit API rate limits. To solve this, the script below uses caching (so it only looks up each unique city-country combination once) and implements a progress-saving mechanism. If the script is stopped or interrupted, you can run it again, and it will pick up right where it left off without losing your data.
# ​1. Prerequisites
​Open your terminal or command prompt and install the required libraries:
```text
pip install pandas geopy requests
```
# 2. Python Script (`add_monthly_weather.py`)
​Create a new file named `add_monthly_weather.py` in the same directory where your world-cities (1).csv file is saved.

# 3. How to Run it:
1. Save your `world-cities (1).csv` file in a dedicated folder.
2. Place the script file `add_monthly_weather.py` into the exact same folder.
3. Open your command terminal, navigate to that folder, and execute:
```text
python add_monthly_weather.py
```

# Important Tips & Expectations:
​Speed: Due to free-tier API restrictions, looking up the location and climate data takes about 1.5 seconds per unique city. If your CSV contains thousands of entries, this script will take several hours to complete.
​Safe Interruption: You don't have to leave it running all at once. You can stop it by pressing `Ctrl + C` inside your terminal. When you run the script again later, it will inspect `world_cities_with_monthly_weather.csv`, see which rows are already complete, and automatically pick up from where you left off.
​Testing: If you want to verify that it outputs correctly first without waiting, you can replace `df = pd.read_csv(input_filename)` with `df = pd.read_csv(input_filename).head(20)` to quickly test the script on just the first 20 cities.
