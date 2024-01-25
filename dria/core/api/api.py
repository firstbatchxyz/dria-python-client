import requests
from typing import Dict, Optional
from dria.config import ConfigBuilder
from dria.exceptions.exceptions import DriaRequestError, DriaNetworkError
from requests.exceptions import RequestException


class API:
    def __init__(self, host: str, api_key: Optional[str] = None):
        """
        Initialize the API client with the provided host and optional API key.

        Args:
            host (str): The API host URL.
            api_key (str, optional): The API key for authentication.
        """
        self.cfg = ConfigBuilder.builder(host=host, api_key=api_key)

    def parse(self, response, request_type: str = ""):
        """
        Parse the HTTP response and check for errors.

        Args:
            response (requests.Response): The HTTP response.
            request_type (str): The type of the HTTP request (e.g., "GET" or "POST").

        Returns:
            dict: The parsed JSON response data.

        Raises:
            DriaRequestError: If the HTTP response status code is not 200.
        """
        if response.status_code != 200:
            raise DriaRequestError(response, request_type)

        return response.json()["data"]

    def get(self, path: str, host: Optional[str] = None):
        """
        Send an HTTP GET request.

        Args:
            path (str): The relative path for the GET request.
            host (str): The host URL.

        Returns:
            Any: The parsed JSON response data.

        Raises:
            DriaRequestError: If the HTTP response status code is not 200 or if a network error occurs.
        """
        url = self._build_url(path, host)
        try:
            response = requests.get(url, headers=self.cfg.headers)
            return self.parse(response, request_type="GET")
        except RequestException as e:
            raise DriaNetworkError(f"Request failed: {e} while making a GET request to {path}")

    def post(self, path: str, host: Optional[str] = None, payload: Dict = None):
        """
        Send an HTTP POST request.

        Args:
            path (str): The relative path for the POST request.
            host (str): The host URL.
            payload (Dict, optional): The JSON payload for the POST request.

        Returns:
            Any: The parsed JSON response data.

        Raises:
            DriaRequestError: If the HTTP response status code is not 200 or if a network error occurs.
        """
        url = self._build_url(path, host)
        try:
            response = requests.post(url, json=payload, headers=self.cfg.headers)
            return self.parse(response, request_type="POST")
        except RequestException as e:
            raise DriaNetworkError(f"Request failed: {e} while making a POST request to {path}")

    def _build_url(self, path: str, host: Optional[str] = None) -> str:
        """
        Build the complete URL based on the host and relative path.

        Args:
            path (str): The relative path for the URL.
            host (str): The host URL. If host is None, the default host from the configuration will be used or override.

        Returns:
            str: The complete URL.
        """
        host = host or self.cfg.host
        return f'https://{host}{path}'
