
import pandas as pd
import requests
import json

url = "https://fr24api.flightradar24.com/api/flight-tracks"
#we need a big list here (consist of dicts) to name all the flight ids we want to query
#the big problem is that we need to know the flight ids in advance

all_flight_ids = [{},{}, {}, {}, {}, {}, {}, {}, {}, {}]  # Add more flight IDs as needed




headers = {
  'Accept': 'application/json',
  'Accept-Version': 'v1',
  'Authorization': 'Bearer 01987b37-5476-7204-8803-dc717f142c7b|yMM8qA7OtUEvaitamX9VWfJqS7rNUsOTT7rsXhAe8e60cbef'
}

def get_flight_tracks(params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=4))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return data

def parse_track_data(track_data):
    if not track_data:
        return []

    parsed_data = pd.DataFrame()
    for flight_id, tracks in track_data[0].items():
        for track in tracks:
            if 'lat' in track and 'lon' in track:
                parsed_data = parsed_data.append({
                    'flight_id': flight_id,
                    'latitude': track['lat'],
                    'longitude': track['lon'],
                    'altitude': track.get('alt', None),
                    'gspeed': track.get('gspeed', None),
                    'vspeed': track.get('vspeed', None),
                    'callsign': track.get('callsign', None),
                    'squawk': track.get('squawk', None),
                    'timestamp': track.get('timestamp', None)
                }, ignore_index=True)
    return parsed_data

if __name__ == "__main__":
    # Fetch flight tracks for all flight IDs
    all_flight_data = list(map(get_flight_tracks, all_flight_ids))
    # Parse the flight track data
    parsed_flight_data = pd.concat(list(map(parse_track_data, all_flight_data)),ignore_index=True)
    
    parsed_flight_data.to_csv('flight_tracks.csv', index=False)
    
    