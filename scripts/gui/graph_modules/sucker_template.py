import requests  # Import any required libraries
from datetime import datetime

def read_datasucker_options():
    """
    Returns a dictionary of configurable options for the datasucker module.
    """
    settings_dict = {
        # Example numeric input
        "numeric_setting": 0,  # Default value

        # Example text input
        "text_setting": "",  # Default empty string

        # Example date inputs
        "start_date": "DATE$",  # Use "DATE$" to prompt for a date input
        "end_date": "DATE$NOW",  # Use "DATE$NOW" for current date/time

        # Example dropdown menu
        "dropdown_setting": [
            "Option 1",  # Default value
            "Option 2",
            "Option 3"
        ],

        # Example API key input
        "api_key": "",  # Prompt for an API key if required
    }
    return settings_dict

def read_description():
    """
    Provides a description of the data source, available data options, and licensing information.
    """
    description = (
        "This module retrieves data from [Data Source Name]. "
        "It allows you to fetch information such as [Data Types]. "
        "Please ensure you have the necessary permissions and API keys if required. "
        "For more information, visit [Data Source Website]."
    )
    return description

def suckdata(settings_dict=None):
    """
    Fetches data based on the provided settings.

    Parameters:
        settings_dict (dict): A dictionary containing the settings as defined in read_datasucker_options().

    Returns:
        tuple: (selected_key, data)
            - selected_key (str): The key or description of the data retrieved.
            - data (list): A list of (datetime, value) tuples.
    """
    if settings_dict is None:
        settings_dict = read_datasucker_options()

    # Extract settings
    numeric_setting = settings_dict.get("numeric_setting")
    text_setting = settings_dict.get("text_setting")
    start_date = settings_dict.get("start_date")
    end_date = settings_dict.get("end_date")
    dropdown_setting = settings_dict.get("dropdown_setting")
    api_key = settings_dict.get("api_key")

    # Validate and process dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Date format should be 'YYYY-MM-DD HH:MM'. Check your input.")

    # Ensure start date is before end date
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    # Prepare API request or data retrieval logic
    # For example, construct API endpoint and parameters
    api_endpoint = "https://api.example.com/data"
    params = {
        "numeric": numeric_setting,
        "text": text_setting,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "option": dropdown_setting,
    }
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Make API request or read data from a local source
    response = requests.get(api_endpoint, params=params, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses

    # Process the retrieved data
    api_data = response.json()
    data = []
    for item in api_data.get("results", []):
        date_str = item.get("timestamp")
        value = item.get("value")
        if date_str and value is not None:
            date_time = datetime.fromisoformat(date_str)
            data.append((date_time, value))

    if not data:
        raise ValueError("No data found for the given parameters.")

    # Define the selected key or description
    selected_key = f"Data for {dropdown_setting}"

    # Return the selected key and data
    return selected_key, data
