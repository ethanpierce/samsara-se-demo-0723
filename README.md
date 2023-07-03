# Samsara Fleet Management Data Analyzer

This script interacts with the Samsara API to fetch and visualize data for a specific vehicle and its trips over a certain number of days. The script extracts information about the vehicle, its trips, and the readings from its temperature sensors.

## Prerequisites

Before you can run this script, you need to install the following Python libraries:

- `requests`
- `time`
- `json`
- `matplotlib`
- `pandas`
- `datetime`
- `google.colab` *optional unless running from google colab notebook*

You can install these using pip:

```bash
pip install requests matplotlib pandas google-colab
```
Note: The datetime and json libraries are built into Python and do not need to be installed separately.

## Usage

Before running the script, ensure you have your Samsara API key stored in a text file. Update the path in the script to the location of this file.

When running the script, you will be prompted to enter the name of the vehicle you're interested in and the number of days you want to analyze from today's date.

The script will fetch the vehicle's information, its trips, and the readings from its temperature sensors. It then plots the temperature sensor readings for each trip.

## Functions

Here's a brief overview of what each function in the script does:

- `get_vehicle_info(vehicle_name, bearerKey)`: Fetches information about a specific vehicle from the Samsara API.
- `get_vehicle_trips(vehicle_info, num_days)`: Fetches information about a vehicle's trips over a certain number of days from the Samsara API.
- `process_trips(trips, vehicle_info)`: Processes the trips and temperature sensor readings, and plots the temperature sensor readings for each trip.
