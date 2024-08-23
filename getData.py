import os
import requests
import json

# List of mission IDs
mission_ids = [
    "66c502f660098b1260afe363",
    "66c502fa60098b1260afe4ff",
    "66bfc00162ab006d367d3cc4"
]

# Base URL
base_url = "https://wfh1llc30j.execute-api.us-east-2.amazonaws.com"


# Function to download and save data in a JSON file
def download_and_save_json(url, save_path, filename):
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        # Ensure the directory exists
        os.makedirs(save_path, exist_ok=True)
        # Save the JSON file directly in the correct folder
        file_path = os.path.join(save_path, filename)
        with open(file_path, 'w') as f:
            f.write(response.text)
        print(f"{filename} downloaded successfully and saved in {save_path}.")
        return response.json()
    else:
        print(f"Error downloading from {url}: {response.status_code}")
        return None


# Download mission data and save in separate folders
for mission_id in mission_ids:
    mission_url = f"{base_url}/missions/{mission_id}"

    # Download mission data
    mission_data = download_and_save_json(mission_url, ".", "mission.json")

    if mission_data and 'name' in mission_data:
        mission_name = mission_data['name']
        mission_folder = os.path.join(".", mission_name)

        # Move the mission JSON into the mission folder
        os.makedirs(mission_folder, exist_ok=True)
        os.rename("mission.json", os.path.join(mission_folder, "mission.json"))

        # Download collection events associated with the mission
        collection_events_url = f"{base_url}/collectionEvents?missionIds={mission_id}&limit=0&skip=0"
        collection_events = download_and_save_json(collection_events_url, mission_folder, "collectionevent.json")

        # Initialize an empty list to store all data
        all_data = []

        # Check if there are collection events
        if collection_events and isinstance(collection_events, list):
            for event in collection_events:
                # Use `_id` to get the ID of the collection event
                event_id = event.get('_id')
                print(f"Event ID: {event_id}")  # Print the event_id to verify it is correct

                if event_id:
                    # Download data associated with the collection events using the correct URL
                    data_url = f"{base_url}/collectionEvents/{event_id}/data?limit=0&skip=0"
                    data_response = requests.get(data_url, headers={'accept': 'application/json'})

                    if data_response.status_code == 200:
                        event_data = data_response.json()
                        all_data.extend(event_data)  # Combine all data into one list
                    else:
                        print(f"Error downloading data for event {event_id}: {data_response.status_code}")

            # Save all combined data into a single file
            data_file_path = os.path.join(mission_folder, "data.json")
            with open(data_file_path, 'w') as f:
                json.dump(all_data, f)
            print(f"All data combined and saved in {data_file_path}.")
        else:
            print(f"No collection events found for mission {mission_id}.")
