import requests
from datetime import datetime

def read_datasucker_options():
    """
    Returns a dictionary of configurable options for the data-sucker module.
    """
    settings_dict = {
        "site": "",  # USGS Site identification number
        "start": "DATE$",  # Start date/time in "YYYY-MM-DD HH:MM" format
        "end": "DATE$NOW",  # End date/time in "YYYY-MM-DD HH:MM" format
        "parameter": [
            "00060 - Discharge, cubic feet per second",
            "00065 - Gage height, feet",
            "00010 - Temperature, water, degrees Celsius",
            "00300 - Dissolved oxygen, mg/L",
            "00400 - pH",
            "63680 - Turbidity, Formazin Nephelometric Units"
        ]  # Available parameters with codes and descriptions
    }
    return settings_dict

def read_description():
    """
    Provides a description of the data source, available parameters, and licensing information.
    """
    description = (
        "This module retrieves recent water data from the USGS National Water Information System (NWIS). "
        "Users can obtain data such as water height (gage height), flow rate (discharge), water temperature, "
        "dissolved oxygen, pH, and turbidity by specifying the USGS Site identification number. "
        "The data can be fetched for a specified date range. Available parameters include:\n"
        "- **00060**: Discharge, cubic feet per second\n"
        "- **00065**: Gage height, feet\n"
        "- **00010**: Temperature, water, degrees Celsius\n"
        "- **00300**: Dissolved oxygen, mg/L\n"
        "- **00400**: pH\n"
        "- **63680**: Turbidity, Formazin Nephelometric Units\n\n"
        "Data is provided by the USGS and is publicly available. "
        "For more information, visit https://waterservices.usgs.gov/."
    )
    return description

def suckdata(settings_dict=None):
    """
    Fetches water data from the USGS NWIS based on provided settings.

    Parameters:
        settings_dict (dict): A dictionary with the following keys:
            - site (str): USGS Site identification number
            - start (str): Start datetime in "YYYY-MM-DD HH:MM" format
            - end (str): End datetime in "YYYY-MM-DD HH:MM" format
            - parameter (str): Selected parameter (e.g., '00060 - Discharge, cubic feet per second')

    Returns:
        tuple: (selected_key, data)
            - selected_key (str): Selected parameter code
            - data (list): A list of (datetime, value) tuples.
    """
    if settings_dict is None:
        settings_dict = read_datasucker_options()

    site = settings_dict.get("site")
    start = settings_dict.get("start")
    end = settings_dict.get("end")
    parameter_selection = settings_dict.get("parameter")

    if not site:
        raise ValueError("Site identification number is required.")

    if not parameter_selection:
        raise ValueError("Parameter is required.")

    # Extract parameter code from selection
    parameter_code = parameter_selection.split(' - ')[0]

    # Convert start and end times to ISO format
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Date format should be 'YYYY-MM-DD HH:MM'. Check your input.")

    # Ensure that start date is not after end date
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    # Build request parameters
    params = {
        "format": "json",
        "sites": site,
        "startDT": start_dt.strftime("%Y-%m-%dT%H:%M"),
        "endDT": end_dt.strftime("%Y-%m-%dT%H:%M"),
        "parameterCd": parameter_code,
        "siteStatus": "all"
    }

    # Make API call
    base_url = "https://waterservices.usgs.gov/nwis/iv/"
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise ValueError(f"API request failed: {response.status_code} - {response.text}")

    api_data = response.json()

    # Extract time series data
    try:
        time_series = api_data['value']['timeSeries'][0]['values'][0]['value']
        variable_description = api_data['value']['timeSeries'][0]['variable']['variableDescription']
    except (KeyError, IndexError):
        raise ValueError("No data found for the given parameters.")

    data = []
    for entry in time_series:
        date_time_str = entry['dateTime']
        value_str = entry['value']

        # Parse datetime
        try:
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S%z")

        # Convert value to float if possible
        try:
            value = float(value_str)
        except ValueError:
            value = None  # Handle missing or non-numeric values

        if value is not None:
            data.append((date_time, value))

    if not data:
        raise ValueError("No valid data points found for the given parameters.")

    selected_key = parameter_code

    # Sort data by date
    data.sort(key=lambda x: x[0])

    return selected_key, data






