# Import necessary libraries
import requests  # for making HTTP requests
import time  # for time-related functions
import json  # for JSON handling
import matplotlib.pyplot as plt  # for plotting data
import pandas as pd  # for data manipulation
from datetime import datetime, timedelta  # for date-time related operations


# Open the file that contains the API key
# The key is read and stored in the variable 'api_key'
# Any newline characters in the file are removed with the replace function
#for your text file that contains ONLY the samsara api key change the path in the open() function
with open('/Users/ethan/Library/CloudStorage/GoogleDrive-ethan.alexander.pierce@gmail.com/My Drive/Projects/samsara-key/api_key.txt', 'r') as file:
    api_key = file.read().strip()
# Format the bearer token for authorization
# The token is used for authenticating the client (this script) with the server (Samsara)
bearerKey = "Bearer " + api_key

# Function to get vehicle trips for a given vehicle and number of days
# It takes in a vehicle_info dictionary and num_days as parameters
def get_vehicle_trips(vehicle_info, num_days):
    # The vehicle_id is extracted from the vehicle_info dictionary
    vehicle_id = vehicle_info["id"]

    # Set up the headers for the HTTP request
    headers = {
        'Accept': 'application/json',
        'Authorization': bearerKey,
        'Host': 'api.samsara.com'
    }

    # Calculate the start and end times for the data to be fetched
    endMs = int(time.time() * 1000)  # Current time in milliseconds
    # The start time is num_days before the end time
    startMs = endMs - num_days * 24 * 60 * 60 * 1000  # Subtract num_days days in milliseconds

    # Format the URL for the API request with the vehicle_id and start and end times
    url = f"https://api.samsara.com/v1/fleet/trips?vehicleId={vehicle_id}&startMs={startMs}&endMs={endMs}"

    # Make the GET request to the API with the headers
    response = requests.get(url, headers=headers)

    # Check the status code of the response
    # If it's not 200, then the request has failed, and return None
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return None

    # If the status code is 200, then the request is successful
    # Parse the JSON response and return it
    data = json.loads(response.text)

    return data

# Function to get vehicle info for a given vehicle name and bearer token
def get_vehicle_info(vehicle_name, bearerKey):
    # The URL for the API request
    url = "https://api.samsara.com/fleet/vehicles?limit=512"

    # The headers for the API request
    headers = {
        "Accept": "application/json",
        "Authorization": bearerKey
    }

    # Make the GET request to the API with the headers
    response = requests.get(url, headers=headers)

    # If the status code is 200, the request is successful
    if response.status_code == 200:
        # Parse the JSON response
        vehicles = response.json().get('data', [])
        # Loop through each vehicle in the response
        for vehicle in vehicles:
            # If the name of the vehicle matches the given vehicle_name, store the vehicle's info and return it
            if vehicle.get('name') == vehicle_name:
                vehicle_info = {
                    "id": vehicle.get('id'),
                    "vin": vehicle.get('vin'),
                    "assigned_driver": vehicle.get('staticAssignedDriver', {}),
                    "temperature_sensors": [
                        {
                            "position": area.get('position'),
                            "sensor_id": sensor.get('id')
                        }
                        for area in vehicle.get('sensorConfiguration', {}).get('areas', [])
                        for sensor in area.get('temperatureSensors', [])
                    ]
                }
                return vehicle_info

        # If the loop completes and no vehicle is found, print an error message and return None
        print("Vehicle not found.")
        return None
    else:
        # If the status code is not 200, the request has failed
        # Print an error message and return None
        print(f"API request failed with status code {response.status_code}")
        return None

# Function to process the trips for a given set of trips and vehicle_info
def process_trips(trips, vehicle_info):
    # The URL for the API request
    url = "https://api.samsara.com/v1/sensors/history"

    # The headers for the API request
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearerKey
    }

    # Loop over each trip in the trips dictionary
    for i, trip in enumerate(trips['trips']):
        # Print some info about the trip
        print(f"Trip {i+1}:")
        print(f"Start: {datetime.utcfromtimestamp(trip['startMs'] / 1000)} at {trip['startLocation']}")
        print(f"End: {datetime.utcfromtimestamp(trip['endMs'] / 1000)} at {trip['endLocation']}")

        # Loop over each temperature sensor in the vehicle_info dictionary
        for sensor in vehicle_info['temperature_sensors']:
            # The payload for the POST request
            payload = {
                "fillMissing": "withNull",
                "series": [{"field": "ambientTemperature", "widgetId": sensor['sensor_id']}],
                "stepMs": 60000,
                "startMs": trip['startMs'],
                "endMs": trip['endMs']
            }

            # Make the POST request to the API with the headers and payload
            response = requests.post(url, headers=headers, json=payload)

            # Parse the JSON response
            data = response.json()

            # Initialize lists to store time and temperature data
            times = []
            temps = []

            # Loop over each result in the data
            for result in data['results']:
                # Convert the time from milliseconds to seconds and then to a datetime object, and add it to the times list
                time = datetime.utcfromtimestamp(result['timeMs'] / 1000)
                times.append(time)

                # Convert the temperature from millicelsius to celsius and add it to the temps list
                # If the temperature is None, add None to the temps list
                temp = result['series'][0] / 1000 if result['series'][0] is not None else None
                temps.append(temp)

            # Plot the time and temperature data for the trip and sensor
            plt.figure(i)
            plt.plot(times, temps, label=f"{sensor['position']} sensor")
            plt.xlabel('Time')
            plt.ylabel('Temperature (Celsius)')
            plt.title(f'Temperature Sensor History for Trip {i+1}')
            plt.legend()
        # Display the plot
        plt.show()

# Main function
def main():
    # Prompt the user to enter the name of the vehicle
    vehicle_name = input("Enter the name of the vehicle: ")

    # Get the info of the vehicle
    vehicle_info = get_vehicle_info(vehicle_name, bearerKey)

    # If vehicle_info is not None, meaning the vehicle was found, print some info about the vehicle
    if vehicle_info is not None:
        print("Vehicle ID: ", vehicle_info["id"])
        print("VIN: ", vehicle_info["vin"])
        print("Assigned Driver ID: ", vehicle_info["assigned_driver"].get('id'))
        print("Assigned Driver Name: ", vehicle_info["assigned_driver"].get('name'))
        print("Temperature Sensors: ")
        for sensor in vehicle_info["temperature_sensors"]:
            print(f"Position: {sensor['position']}, Sensor ID: {sensor['sensor_id']}")

        # You can pass vehicle_info or any of its properties into another function here
        # Another example function could be called here
        # another_function(vehicle_info["id"])

    # Prompt the user to enter the number of days to go back from today's date
    num_days = input("Enter the number of days to go back from today's date ")

    # Get the vehicle trips for the given vehicle and number of days
    data = get_vehicle_trips(vehicle_info, int(num_days))

    # Process the trips
    process_trips(data, vehicle_info)

# This line ensures that the main function is only called if this script is being run directly
# If it's being imported as a module in another script, then the main function won't be called
if __name__ == "__main__":
    main()
