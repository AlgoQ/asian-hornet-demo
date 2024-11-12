from pprint import pprint
import time
import requests
from models import Observation, Photo
from datetime import datetime

from config import BASE_URL


class INaturalistProvider:
    def fetch_raw_inaturalist_observations(self, page, since=None):
        place_id = "7008"  # Belgium
        taxon_name = "Vespa+velutina"
        url = (
            f"https://api.inaturalist.org/v1/observations?"
            f"taxon_name={taxon_name}&place_id={place_id}&per_page=200&page={page}"
            f"&photos=true"
        )
        if since:
            url += f"&created_since={since}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        
        # TODO: Custom error handling
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching observations: {http_err} - Response: {response.text}")
            return {}
        except Exception as err:
            print(f"An error occurred while fetching observations: {err}")
            return {}

    def parse_observations(self, raw_data) -> list[Observation]:
        observations = []
        for result in raw_data["results"]:
            photos = []
            if result.get("photos"):
                for photo in result["photos"]:
                    photo_url = photo.get("medium_url", photo.get("url", ""))
                    photo_url = photo_url.replace("square", "medium")

                    photos.append(
                        Photo(
                            id=photo["id"],
                            url=photo_url,
                            license_code=photo.get("license_code", ""),
                            attribution=photo.get("attribution", ""),
                        )
                    )

            observed_on = None
            if time_str := result.get("time_observed_at"):
                try:
                    dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    observed_on = int(dt.timestamp())
                except (ValueError, TypeError):
                    pass

            full_name = result["user"].get("name_autocomplete", "")

            observation = Observation(
                external_id=result["id"],
                observed_on=observed_on,
                description=result.get("description", ""),
                latitude=result["geojson"]["coordinates"][1],
                longitude=result["geojson"]["coordinates"][0],
                observer=full_name if full_name else result["user"].get("login", ""),
                place=result.get("place_guess", ""),
                photos=photos
            )
            observations.append(observation)
        return observations

    def post_observations(self, observations: list[Observation]):
        data = [observation.model_dump() for observation in observations]
        url = f"{BASE_URL}/observations"
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            created_observations_ids = response.json()
            for obs, created_obs_id in zip(observations, created_observations_ids):                
                if not created_obs_id:
                    continue
                if obs.photos:
                    self.post_photos(obs.photos, created_obs_id)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error while posting observations: {http_err} - Response: {response.text}")
        except Exception as err:
            print(f"Unexpected error while posting observations: {err}")

    def post_photos(self, photos: list[Photo], observation_id: int):
        url = f"{BASE_URL}/photos"
        photo_data = [photo.model_dump(exclude={"observation_id"}) for photo in photos]
        for photo in photo_data:
            photo["observation_id"] = observation_id
        try:
            response = requests.post(url, json=photo_data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error while posting photos: {http_err} - Response: {response.text}")
        except Exception as err:
            print(f"Unexpected error while posting photos: {err}")

    def get_latest_observation(self):
        url = f"{BASE_URL}/observations"
        response = requests.get(url, params={"page": 1, "per_page": 1})
        if response.status_code == 200 and response.json():
            return response.json()[0]
        return None

provider = INaturalistProvider()
latest_observation = provider.get_latest_observation()
since = latest_observation["observed_on"] if latest_observation else None

page = 1
total_results = 1
results_per_page = 200

while (page - 1) * results_per_page < total_results:
    print(f"Fetching page {page}...")
    raw_data = provider.fetch_raw_inaturalist_observations(page, since)
    curr_results = len(raw_data["results"])
    total_results = raw_data["total_results"]
    observations = provider.parse_observations(raw_data)
    provider.post_observations(observations)
    print(f"Posted {results_per_page} observations. Progress: {round(page * results_per_page / total_results * 100)}%")
    page += 1
    time.sleep(1)
