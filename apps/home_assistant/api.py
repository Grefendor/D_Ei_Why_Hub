import requests
import json

class HomeAssistantAPI:
    """
    Handles communication with the Home Assistant REST API.
    """
    def __init__(self, url, token, demo_mode=False):
        """
        Initializes the API client.

        Args:
            url (str): The base URL of the Home Assistant instance (e.g., http://homeassistant.local:8123).
            token (str): The Long-Lived Access Token.
            demo_mode (bool): If True, uses simulated data instead of real API calls.
        """
        self.url = url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.demo_mode = demo_mode

    def check_connection(self):
        """
        Verifies if the API is reachable and the token is valid.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        if self.demo_mode:
            return True
            
        try:
            response = requests.get(f"{self.url}/api/", headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_states(self):
        """
        Retrieves the states of all entities.

        Returns:
            list: A list of entity state dictionaries, or an empty list if the request fails.
        """
        if self.demo_mode:
            return self._get_demo_states()

        try:
            response = requests.get(f"{self.url}/api/states", headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException as e:
            print(f"Error fetching states: {e}")
            return []

    def call_service(self, domain, service, service_data=None):
        """
        Calls a service in Home Assistant.

        Args:
            domain (str): The domain of the service (e.g., "light", "switch").
            service (str): The service name (e.g., "turn_on", "toggle").
            service_data (dict, optional): Additional data for the service call (e.g., {"entity_id": "light.living_room"}).

        Returns:
            bool: True if the call was successful, False otherwise.
        """
        if self.demo_mode:
            print(f"[DEMO] Calling service {domain}.{service} with {service_data}")
            return True

        try:
            url = f"{self.url}/api/services/{domain}/{service}"
            response = requests.post(url, headers=self.headers, json=service_data or {}, timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error calling service {domain}.{service}: {e}")
            return False

    def _get_demo_states(self):
        """
        Returns simulated entity states for demo mode.
        """
        return [
            {
                "entity_id": "light.living_room",
                "state": "on",
                "attributes": {"friendly_name": "Living Room Light"}
            },
            {
                "entity_id": "light.kitchen",
                "state": "off",
                "attributes": {"friendly_name": "Kitchen Light"}
            },
            {
                "entity_id": "switch.coffee_maker",
                "state": "off",
                "attributes": {"friendly_name": "Coffee Maker"}
            },
            {
                "entity_id": "sensor.temperature",
                "state": "21.5",
                "attributes": {"friendly_name": "Living Room Temp", "unit_of_measurement": "°C"}
            },
            {
                "entity_id": "binary_sensor.front_door",
                "state": "off",
                "attributes": {"friendly_name": "Front Door"}
            },
            {
                "entity_id": "person.lasse",
                "state": "home",
                "attributes": {"friendly_name": "Lasse"}
            },
            {
                "entity_id": "sun.sun",
                "state": "above_horizon",
                "attributes": {"friendly_name": "Sun"}
            }
        ]
