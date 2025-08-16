import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import List
import time

def bounds_dict_to_string(bounds: dict) -> str:
    """Convert a bounds dict to FR24 API string format."""
    return f"{bounds['north']},{bounds['south']},{bounds['west']},{bounds['east']}"

def fetch_historic_flight_positions(api_token: str, start_date: datetime, end_date: datetime,
                                    bounds_list: List[dict], interval_seconds: int = 15*60,
                                    limit: int = 300, **filters) -> List[dict]:
    """
    Fetches historical flight positions for multiple bounds rectangles.
    """
    api_url = 'https://fr24api.flightradar24.com/api/historic/flight-positions/full'
    headers = {
        'Accept': 'application/json',
        'Accept-Version': 'v1',
        'Authorization': f'Bearer {api_token}'
    }

    # Prepare timestamps
    timestamps = []
    current_time = start_date
    delta = timedelta(seconds=interval_seconds)
    while current_time <= end_date:
        timestamps.append(int(current_time.timestamp()))
        current_time += delta

    all_data = []

    # Initialize queue with all bounds
    bounds_to_check = [bounds_dict_to_string(b) for b in bounds_list]

    while bounds_to_check:
        current_bounds = bounds_to_check.pop(0)
        for ts in timestamps:
            params = {
                'timestamp': ts,
                'bounds': current_bounds,
                'limit': limit
            }
            params.update(filters)

            response = requests.get(api_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"Timestamp {ts}, Bounds {current_bounds}: Retrieved {len(data)} records")

                if len(data) < limit:
                    all_data.extend(data)
                else:
                    # 超过 limit，拆分成四个小矩形
                    north, south, west, east = map(float, current_bounds.split(','))
                    mid_lat = (north + south) / 2
                    mid_lon = (west + east) / 2
                    bounds_to_check.extend([
                        f"{north},{mid_lat},{west},{mid_lon}",  # NW
                        f"{north},{mid_lat},{mid_lon},{east}",  # NE
                        f"{mid_lat},{south},{west},{mid_lon}",  # SW
                        f"{mid_lat},{south},{mid_lon},{east}"   # SE
                    ])
                    print(f"Warning: More than {limit} records, splitting bounds")

            elif response.status_code == 429:
                wait = int(response.headers.get('Retry-After', 60))
                print(f"Rate limit reached. Sleeping for {wait} seconds.")
                time.sleep(wait)
                response = requests.get(api_url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    all_data.extend(data)
                    print(f"Timestamp {ts} (retry): Retrieved {len(data)} records")
                else:
                    print(f"Error {response.status_code} for timestamp {ts} after retry")
            else:
                print(f"Error {response.status_code} for timestamp {ts}")

    return all_data

# ------------------ Example Usage ------------------
if __name__ == "__main__":
    with open("token.txt", "r", encoding="utf-8") as f:
        API_TOKEN = f.read().strip()
    start_date = datetime(2025, 7, 28, 0, 0, 0)
    end_date = datetime(2025, 8, 4, 0, 0, 0)
    interval_seconds = 60*60

    with open('query_format_YangtzeDelta.json', 'r') as f:
        bounds_list = json.load(f)

    all_flights = fetch_historic_flight_positions(
        api_token=API_TOKEN,
        start_date=start_date,
        end_date=end_date,
        bounds_list=bounds_list,
        interval_seconds=interval_seconds,
        limit=300
    )

    all_flights_df = pd.DataFrame(all_flights)
    all_flights_df.to_csv('historic_flight_positions.csv', index=False)

    print(f"Total records retrieved: {len(all_flights)}")
    