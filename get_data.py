import os
import requests

# List of mission IDs
mission_ids = [
    "66c5031060098b1260afe7d0",
    "66c5032560098b1260afed72"
]

# Base URL
base_url = "https://wfh1llc30j.execute-api.us-east-2.amazonaws.com"


# Function to download and save data from a URL
def download_file(url, save_path, filename):
    response = requests.get(url)
    if response.status_code == 200:
        # Ensure the directory exists
        os.makedirs(save_path, exist_ok=True)
        # Save the file directly in the correct folder
        file_path = os.path.join(save_path, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"{filename} downloaded successfully and saved in {save_path}.")
    else:
        print(f"Error downloading from {url}: {response.status_code}")


# Download the CSV files associated with each mission
for mission_id in mission_ids:
    print(f"Processing mission ID: {mission_id}")

    # Step 1: Get the collection events for the mission
    collection_events_url = f"{base_url}/collectionEvents?missionIds={mission_id}&limit=0&skip=0"
    collection_events = requests.get(collection_events_url, headers={'accept': 'application/json'}).json()

    if collection_events and isinstance(collection_events, list) and len(collection_events) > 0:
        # Step 2: Get the first collection event
        first_event = collection_events[0]
        event_id = first_event.get('_id')
        print(f"Processing Collection Event ID: {event_id}")

        if event_id:
            # Step 3: Get the data records for the first collection event
            data_url = f"{base_url}/collectionEvents/{event_id}/data?limit=0&skip=0"
            data_response = requests.get(data_url, headers={'accept': 'application/json'})

            if data_response.status_code == 200:
                event_data = data_response.json()
                if event_data and len(event_data) > 0:
                    # Step 4: Get the 'filepath' from the first data record
                    filepath = event_data[0].get('filepath')
                    if filepath:
                        # Use mission_id or event_id to create a unique filename
                        filename = f"{mission_id}.csv"
                        # Download the CSV file
                        download_file(filepath, ".", filename)
                    else:
                        print(f"No filepath found in the first data record for event {event_id}.")
            else:
                print(f"Error downloading data for event {event_id}: {data_response.status_code}")
    else:
        print(f"No collection events found for mission {mission_id}.")
