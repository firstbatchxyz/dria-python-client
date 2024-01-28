class DriaException(Exception):
    """Base exception class for Dria-related exceptions."""


class DriaConfigurationError(DriaException):
    def __init__(self, msg: str):
        """
        Exception for configuration errors.

        Args:
            msg (str): The exception message.
        """
        super().__init__(msg)


class DriaParameterError(DriaException):
    def __init__(self, msg: str):
        """
        Exception for parameter errors.

        Args:
            msg (str): The exception message.
        """
        super().__init__(msg)


class DriaNetworkError(DriaException):
    def __init__(self, msg: str):
        """
        Exception for API errors.

        Args:
            msg (str): The exception message.
        """
        super().__init__(msg)


class DriaRequestError(DriaException):
    def __init__(self, response, request_type: str):
        """
        Exception for request errors.

        Args:
            response: The HTTP response object.
            request_type (str): The type of the HTTP request (e.g., "GET" or "POST").
        """
        if response.status_code == 401 or response.status_code == 403 or response.status_code == 402:
            msg = f"Unauthorized request {response.text} while making a {request_type} function"
        elif response.status_code == 404:
            msg = f"Not found {response.text} while making a {request_type} function"
        else:
            msg = f"Request failed with status code {response.status_code} while making a {request_type} function: {response.text}"

        super().__init__(msg)
