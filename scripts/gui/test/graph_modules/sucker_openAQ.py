import requests
from datetime import datetime

def read_datasucker_options():
    """
    Returns a dictionary of configurable options for the data-sucker module.
    """
    settings_dict = {
        "api_key": "",  # User's OpenAQ API key
        "location_type": ["coordinates", "city"],  # Choose between 'coordinates' or 'city'
        "latitude": 51.5074,  # Default latitude (London)
        "longitude": -0.1278,  # Default longitude (London)
        "radius": 5000,  # Radius in meters for coordinate search
        "country": "",  # Country code (e.g., 'GB' for the United Kingdom)
        "city": "",  # City name
        "start": "DATE$",  # Default start date/time (string format)
        "end": "DATE$NOW",  # Default end date/time (string format)
        "parameter": [
            "pm25",
            "pm10",
            "no2",
            "so2",
            "co",
            "o3",
            "bc"
        ]  # Available parameters
    }
    return settings_dict

def read_description():
    """
    Provides a concise description of the data source, usage, and license.
    """
    description = (
        "Retrieves air quality data from the OpenAQ API, "
        "OpenAQ is a nonprofit organization providing universal access to air quality data.\n\n"
        "You can select data based on coordinates (latitude and longitude) "
        "or by specifying a country and city.\n"
        "  Available parameters include;\n"
        "    PM2.5 (pm25) Particulate matter less than 2.5 micrometers in diameter mass concentration\n"
        "    PM10 (pm10) Particles less than 10 µm in diameter.\n" 
        "    NO₂ ppb\n" 
        "    SO₂ ppb\n" 
        "    CO ppb\n"
        "    O₃ ppb\n"
        "    Black Carbon (bc) µg/m³\n\n"
        "The data is sourced from official air quality monitoring stations "
        "around the world.\n\n" 
        " OpenAQ data is free to use but now requires an API key.\n"
        " Please obtain an API key from openaq.org and enter it in the settings.\n"
    )
    return description

def suckdata(settings_dict=None):
    """
    Fetches air quality data from the OpenAQ API based on provided settings.

    Parameters:
        settings_dict (dict): A dictionary with the following keys:
            - api_key (str): Your OpenAQ API key
            - location_type (str): 'coordinates' or 'city'
            - latitude (float): Latitude of the location (if location_type is 'coordinates')
            - longitude (float): Longitude of the location (if location_type is 'coordinates')
            - radius (int): Radius in meters (if location_type is 'coordinates')
            - country (str): Country code (if location_type is 'city')
            - city (str): City name (if location_type is 'city')
            - start (str): Start datetime in "YYYY-MM-DD HH:MM" format
            - end (str): End datetime in "YYYY-MM-DD HH:MM" format
            - parameter (str): Selected parameter (e.g., 'pm25')

    Returns:
        tuple: (selected_key, data)
            - selected_key (str): Selected parameter
            - data (list): A list of (datetime, value) tuples.
    """
    if settings_dict is None:
        settings_dict = read_datasucker_options()

    api_key = settings_dict.get("api_key")
    if not api_key:
        raise ValueError("API key is required. Please obtain an API key from OpenAQ and enter it in the settings.")

    location_type = settings_dict.get("location_type", "coordinates")
    parameter = settings_dict.get("parameter", "pm25")
    start = settings_dict.get("start")
    end = settings_dict.get("end")

    # Convert start and end times to ISO format
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Date format should be 'YYYY-MM-DD HH:MM'. Check your input.")

    # Ensure that start date is not after end date
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    # Build query parameters
    params = {
        "parameter": parameter,
        "date_from": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date_to": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 1000,  # Adjust limit as needed
        "page": 1,
    }

    if location_type == "coordinates":
        latitude = settings_dict.get("latitude")
        longitude = settings_dict.get("longitude")
        radius = settings_dict.get("radius", 5000)
        if latitude is None or longitude is None:
            raise ValueError("Latitude and longitude must be provided.")
        params["coordinates"] = f"{latitude},{longitude}"
        params["radius"] = radius
    elif location_type == "city":
        country = settings_dict.get("country")
        city = settings_dict.get("city")
        if not city:
            raise ValueError("City must be provided when location_type is 'city'.")
        params["city"] = city
        if country:
            params["country"] = country
    else:
        raise ValueError("Invalid location type. Must be 'coordinates' or 'city'.")

    # Prepare request headers with API key
    headers = {
        "X-API-Key": api_key
    }

    # Make API call
    base_url = "https://api.openaq.org/v2/measurements"
    data = []
    while True:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        api_data = response.json()
        results = api_data.get("results", [])
        if not results:
            break
        for result in results:
            date_str = result.get("date", {}).get("utc")
            value = result.get("value")
            if date_str and value is not None:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    # Handle date strings without timezone
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                data.append((date, value))
        meta = api_data.get("meta", {})
        page = meta.get("page", 1)
        total_pages = meta.get("totalPages", 1)
        if page >= total_pages:
            break
        else:
            params["page"] = page + 1

    selected_key = parameter
    if not data:
        raise ValueError("No data found for the given parameters.")
    # Sort data by date
    data.sort(key=lambda x: x[0])
    return selected_key, data
