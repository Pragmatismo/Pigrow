import requests
import base64
from datetime import datetime, timedelta

def read_datasucker_options():
    """
    Returns a dictionary of configurable options for the data-sucker module.
    """
    settings_dict = {
        "api_key": "",  # User's AstronomyAPI app_id and app_secret concatenated with a colon (app_id:app_secret)
        "latitude": 51.5074,  # Default latitude (London)
        "longitude": -0.1278,  # Default longitude (London)
        "elevation": 0,  # Elevation in meters
        "start": "DATE$",  # Start date (string format)
        "end": "DATE$NOW",  # End date (string format)
        "body": ["moon", "sun"],  # Celestial body selection
        "parameter": [
            "distance",
            "illumination",
            "phase",
            "elongation",
            "magnitude",
            "altitude",
            "azimuth",
            "positional_angle",
            "right_ascension",
            "declination"
        ]  # Available parameters
    }
    return settings_dict

def read_description():
    """
    Provides a description of the data source, available parameters, and licensing information.
    """
    description = (
        "This module retrieves astronomical data for the Sun and Moon from the AstronomyAPI. "
        "Users can obtain data such as distance from Earth, illumination percentage, phase, "
        "elongation, magnitude, and positional data based on latitude, longitude, and elevation. "
        "The data can be fetched for a specified date range. "
        "Parameters explained:\n"
        "- **Distance**: The distance from Earth to the celestial body in kilometers.\n"
        "- **Illumination**: The fraction of the Moon's disc illuminated by the Sun.\n"
        "- **Phase**: The current phase of the Moon (e.g., New Moon, Full Moon).\n"
        "- **Elongation**: The angular distance between the Sun and Moon as seen from Earth.\n"
        "- **Magnitude**: The brightness of the celestial body as seen from Earth.\n"
        "- **Altitude**: The angle of the celestial body above the horizon.\n"
        "- **Azimuth**: The compass direction from which the celestial body is coming.\n"
        "- **Positional Angle**: The orientation of the celestial body.\n"
        "- **Right Ascension**: The celestial equivalent of longitude.\n"
        "- **Declination**: The celestial equivalent of latitude.\n\n"
        "Note: An API key is required to use the AstronomyAPI. Please obtain an API key from "
        "https://astronomyapi.com/ and enter it in the settings. The API key should be provided "
        "as 'app_id:app_secret'."
    )
    return description

def suckdata(settings_dict=None):
    """
    Fetches astronomical data from the AstronomyAPI based on provided settings.

    Parameters:
        settings_dict (dict): A dictionary with the following keys:
            - api_key (str): Your AstronomyAPI app_id and app_secret concatenated with a colon (app_id:app_secret)
            - latitude (float): Latitude of the location
            - longitude (float): Longitude of the location
            - elevation (float): Elevation in meters
            - start (str): Start date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM" format
            - end (str): End date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM" format
            - body (str): 'moon' or 'sun'
            - parameter (str): Selected parameter to retrieve

    Returns:
        tuple: (selected_key, data)
            - selected_key (str): Selected parameter
            - data (list): A list of (datetime, value) tuples.
    """
    if settings_dict is None:
        settings_dict = read_datasucker_options()

    api_key = settings_dict.get("api_key")
    if not api_key or ':' not in api_key:
        raise ValueError("API key is required and should be in the format 'app_id:app_secret'. Please obtain an API key from AstronomyAPI and enter it in the settings.")

    latitude = settings_dict.get("latitude")
    longitude = settings_dict.get("longitude")
    elevation = settings_dict.get("elevation", 0)
    start_date = settings_dict.get("start")
    end_date = settings_dict.get("end")
    body = settings_dict.get("body", "moon")
    parameter = settings_dict.get("parameter")

    # Adjust date parsing to handle 'YYYY-MM-DD HH:MM' format
    try:
        # Extract the date part if time is included
        start_date_str = start_date.split(' ')[0]
        end_date_str = end_date.split(' ')[0]

        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date format should be 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'. Check your input.")

    # Ensure that start date is not after end date
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    # Prepare authentication
    app_id, app_secret = api_key.split(':', 1)
    credentials = f"{app_id}:{app_secret}"
    credentials_bytes = credentials.encode('ascii')
    base64_bytes = base64.b64encode(credentials_bytes)
    base64_credentials = base64_bytes.decode('ascii')

    headers = {
        "Authorization": f"Basic {base64_credentials}"
    }

    # Initialize data list
    data = []
    date = start_dt
    delta = timedelta(days=1)

    while date <= end_dt:
        date_str = date.strftime("%Y-%m-%d")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation,
            "from_date": date_str,
            "to_date": date_str,
            "time": "00:00:00"
        }

        # API endpoint
        url = f"https://api.astronomyapi.com/api/v2/bodies/positions/{body}"

        # Make API call
        print("making api call")
        response = requests.get(url, params=params, headers=headers)
        print(response)
        if response.status_code != 200:
            raise ValueError(f"API request failed: {response.status_code} - {response.text}")
        api_data = response.json()
        positions = api_data.get("data", {}).get("table", {}).get("rows", [])

        for position in positions:
            print(position)
            date_time_str = position.get("cells", [])[0].get("date", "")
            try:
                # Attempt to parse date with milliseconds and 'Z'
                date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                try:
                    # Attempt to parse date without milliseconds
                    date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    # As a last resort, parse date without 'Z'
                    date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
            info = position.get("cells", [])[0].get("position", {})
            extra_info = position.get("cells", [])[0].get("extraInfo", {})
            phase_info = extra_info.get("phase", {})

            # Map parameter to data
            value = None
            if parameter == "distance":
                value = info.get("distance", {}).get("fromEarth", {}).get("km")
            elif parameter == "illumination":
                value = float(phase_info.get("fraction")) * 100 if phase_info.get("fraction") else None
            elif parameter == "phase":
                value = phase_info.get("string")
            elif parameter == "elongation":
                value = extra_info.get("elongation")
            elif parameter == "magnitude":
                value = extra_info.get("magnitude")
            elif parameter == "altitude":
                value = info.get("horizonal", {}).get("altitude", {}).get("degrees")
            elif parameter == "azimuth":
                value = info.get("horizonal", {}).get("azimuth", {}).get("degrees")
            elif parameter == "positional_angle":
                value = info.get("positionalAngle", {}).get("degrees")
            elif parameter == "right_ascension":
                value = info.get("equatorial", {}).get("rightAscension", {}).get("hours")
            elif parameter == "declination":
                value = info.get("equatorial", {}).get("declination", {}).get("degrees")
            else:
                raise ValueError(f"Invalid parameter selected: {parameter}")

            if value is not None:
                data.append((date_time, value))
        date += delta  # Move to the next day

    selected_key = parameter
    if not data:
        raise ValueError("No data found for the given parameters.")

    # Sort data by date
    data.sort(key=lambda x: x[0])

    return selected_key, data