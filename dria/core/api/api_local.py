import requests
from typing import Dict
from dria.exceptions.exceptions import DriaRequestError, DriaNetworkError
from requests.exceptions import RequestException


class APILocal:

    @staticmethod
    def parse(response, request_type: str = ""):
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

    def get(self, path: str):
        """
        Send an HTTP GET request.

        Args:
            path (str): The relative path for the GET request.

        Returns:
            Any: The parsed JSON response data.

        Raises:
            DriaRequestError: If the HTTP response status code is not 200 or if a network error occurs.
        """
        url = self._build_url(path)
        try:
            response = requests.get(url)
            return self.parse(response, request_type="GET")
        except RequestException as e:
            raise DriaNetworkError(f"Request failed: {e} while making a GET request to {path}")

    def post(self, path: str, payload: Dict = None):
        """
        Send an HTTP POST request.

        Args:
            path (str): The relative path for the POST request.
            payload (Dict, optional): The JSON payload for the POST request.

        Returns:
            Any: The parsed JSON response data.

        Raises:
            DriaRequestError: If the HTTP response status code is not 200 or if a network error occurs.
        """
        url = self._build_url(path)
        try:
            response = requests.post(url, json=payload)
            return self.parse(response, request_type="POST")
        except RequestException as e:
            raise DriaNetworkError(f"Request failed: {e} while making a POST request to {path}")

    @staticmethod
    def _build_url(path) -> str:
        """
        Build the complete URL based on the host and relative path.

        Returns:
            str: The complete URL.
        """
        return f'http://0.0.0.0:8080{path}'
