from dria.exceptions.exceptions import DriaConfigurationError

from typing import NamedTuple, Optional, Dict
import os


class Config(NamedTuple):
    host: str = ""
    headers: Optional[Dict[str, str]] = {}


class ConfigBuilder:
    """
    Initializes the Dria Config.

    :param host: Optional. Controller host.
    :param headers: Optional. Headers to be sent with each request.
    """

    @staticmethod
    def builder(
            host: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> Config:
        api_key = api_key or os.getenv("DRIA_API_KEY")
        host = host
        headers = {'Content-Type': 'application/json',
                   "Accept-Encoding": "gzip, deflate, br",
                   "Connection": "keep-alive",
                   "Accept": "*/*",
                   "x-api-key": api_key}
        if not api_key:
            raise DriaConfigurationError("Not specified an DRIA_API_KEY. Please set it as an environment variable or "
                                         "pass it as an argument")
        if not host:
            raise DriaConfigurationError("You haven't specified a host.")

        return Config(host, headers)
