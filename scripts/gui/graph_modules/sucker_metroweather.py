import requests
from datetime import datetime

def read_datasucker_options():
    """
    Returns a dictionary of configurable options for the data-sucker module.
    Organized with two options lists: 'hourly' and 'daily'.
    """
    settings_dict = {
        "latitude": 51.493847,  # Default latitude
        "longitude": -0.1630249,  # Default longitude
        "start": "DATE$",  # Default start date/time (string format)
        "end": "DATE$NOW",  # Default end date/time (string format)
        "hourly": [
            "Temperature (2 m)",
            "Relative Humidity (2 m)",
            "Dew Point (2 m)",
            "Apparent Temperature",
            "Precipitation Probability",
            "Precipitation",
            "Rain",
            "Showers",
            "Snowfall",
            "Snow Depth",
            "Weather Code",
            "Sea Level Pressure",
            "Surface Pressure",
            "Cloud Cover Total",
            "Cloud Cover Low",
            "Cloud Cover Mid",
            "Cloud Cover High",
            "Visibility",
            "Evapotranspiration",
            "Reference Evapotranspiration",
            "Vapor Pressure Deficit",
            "Wind Speed (10 m)",
            "Wind Direction (10 m)",
            "Wind Gusts (10 m)",
            "Temperature (80 m)",
            "Temperature (120 m)",
            "Temperature (180 m)",
            "Soil Temperature (0 cm)",
            "Soil Temperature (6 cm)",
            "Soil Temperature (18 cm)",
            "Soil Temperature (54 cm)",
            "Soil Moisture (0-1 cm)",
            "Soil Moisture (1-3 cm)",
            "Soil Moisture (3-9 cm)",
            "Soil Moisture (9-27 cm)",
            "Soil Moisture (27-81 cm)",
            ""
        ],
        "daily": [
            "",
            "Weather Code",
            "Maximum Temperature (2 m)",
            "Minimum Temperature (2 m)",
            "Maximum Apparent Temperature (2 m)",
            "Minimum Apparent Temperature (2 m)",
            "Sunrise",
            "Sunset",
            "Daylight Duration",
            "Sunshine Duration",
            "UV Index",
            "UV Index Clear Sky",
            "Precipitation Sum",
            "Rain Sum",
            "Showers Sum",
            "Snowfall Sum",
            "Precipitation Hours",
            "Precipitation Probability Max",
            "Maximum Wind Speed (10 m)",
            "Maximum Wind Gusts (10 m)",
            "Dominant Wind Direction (10 m)",
            "Shortwave Radiation Sum",
            "Reference Evapotranspiration"
        ]
    }
    return settings_dict

def read_description():
    """
    Provides a concise description of the data source, usage, and license.
    """
    description = (
        "This module retrieves historical weather data from the Open-Meteo Historical Weather API. "
        "It supports both hourly and daily variables, including common options like temperature, "
        "humidity, surface pressure, and precipitation, as well as specialized data like soil moisture "
        "and soil temperature. Only one variable can be selected at a time. The data is sourced from "
        "reanalysis datasets such as ERA5, offering high accuracy. Open-Meteo is free to use for "
        "non-commercial purposes, with a limit of 10,000 requests per day.\n\n"
        "For more detailed informaion on available data see https://open-meteo.com/en/docs/historical-weather-api"
    )
    return description

def suckdata(settings_dict=None):
    """
    Fetches weather data from the Open-Meteo Historical Weather API based on provided settings.

    Parameters:
        settings_dict (dict): A dictionary with the following keys:
            - latitude (float): Latitude of the location
            - longitude (float): Longitude of the location
            - start (str): Start datetime in "YYYY-MM-DD HH:MM" format
            - end (str): End datetime in "YYYY-MM-DD HH:MM" format
            - hourly (str): Selected hourly variable (from read_datasucker_options())
            - daily (str): Selected daily variable (from read_datasucker_options())

    Returns:
        tuple: (key, data)
            - key (str): Selected variable name
            - data (list): A list of (datetime, value) tuples for the selected variable.
    """
    if settings_dict is None:
        settings_dict = read_datasucker_options()

    latitude = settings_dict.get("latitude")
    longitude = settings_dict.get("longitude")
    start = settings_dict.get("start")
    end = settings_dict.get("end")
    hourly_key = settings_dict.get("hourly", "")
    daily_key = settings_dict.get("daily", "")

    # Determine the selected key
    if hourly_key:
        granularity = "hourly"
        selected_key = hourly_key
    elif daily_key:
        granularity = "daily"
        selected_key = daily_key
    else:
        raise ValueError("No variable selected for retrieval.")

    # Key mapping for API
    key_mapping = {
        "Temperature (2 m)": "temperature_2m",
        "Relative Humidity (2 m)": "relative_humidity_2m",
        "Dew Point (2 m)": "dewpoint_2m",
        "Apparent Temperature": "apparent_temperature",
        "Precipitation Probability": "precipitation_probability",
        "Precipitation": "precipitation",
        "Rain": "rain",
        "Showers": "showers",
        "Snowfall": "snowfall",
        "Snow Depth": "snow_depth",
        "Weather Code": "weathercode",
        "Sea Level Pressure": "pressure_msl",
        "Surface Pressure": "surface_pressure",
        "Cloud Cover Total": "cloudcover",
        "Cloud Cover Low": "cloudcover_low",
        "Cloud Cover Mid": "cloudcover_mid",
        "Cloud Cover High": "cloudcover_high",
        "Visibility": "visibility",
        "Evapotranspiration": "evapotranspiration",
        "Reference Evapotranspiration": "et0_fao_evapotranspiration",
        "Vapor Pressure Deficit": "vapor_pressure_deficit",
        "Wind Speed (10 m)": "windspeed_10m",
        "Wind Direction (10 m)": "winddirection_10m",
        "Wind Gusts (10 m)": "windgusts_10m",
        "Maximum Temperature (2 m)": "temperature_2m_max",
        "Minimum Temperature (2 m)": "temperature_2m_min",
        "Precipitation Sum": "precipitation_sum",
        "Sunrise": "sunrise",
        "Sunset": "sunset",
        "Shortwave Radiation Sum": "shortwave_radiation_sum",
        "Soil Moisture (0-1 cm)": "soil_moisture_0_1cm",
        "Soil Temperature (0 cm)": "soil_temperature_0cm"
    }

    if selected_key not in key_mapping:
        raise ValueError(f"Selected key '{selected_key}' is not valid.")

    api_key = key_mapping[selected_key]

    # Convert start and end times to ISO format
    try:
        start_iso = datetime.strptime(start.split(".")[0], "%Y-%m-%d %H:%M").isoformat()
        end_iso = datetime.strptime(end.split(".")[0], "%Y-%m-%d %H:%M").isoformat()
    except ValueError:
        raise ValueError("Date format should be 'YYYY-MM-DD HH:MM'. Check your input.")

    # Formulate API request
    base_url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_iso.split("T")[0],
        "end_date": end_iso.split("T")[0],
        granularity: api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    api_data = response.json()

    # Extract and format data
    if granularity in api_data:
        times = [datetime.fromisoformat(d) for d in api_data[granularity]["time"]]
        values = api_data[granularity].get(api_key, [])
        data = list(zip(times, values))
    else:
        raise ValueError(f"No data found for {selected_key}.")

    return selected_key, data
