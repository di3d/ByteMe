import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, **kwargs):
    """A simple wrapper for requests methods.
    
    Args:
        url: the url of the http service
        method: the http method
        json: the JSON input when needed by the http method
        **kwargs: any additional parameters for the request
        
    Returns:
        The JSON reply content from the http service if the call succeeds;
        otherwise, returns a JSON object with error details.
    """
    logger.info(f"Invoking {method} request to {url}")
    if json:
        logger.debug(f"Payload: {json}")
        
    try:
        if method.upper() in SUPPORTED_HTTP_METHODS:
            response = requests.request(method, url, json=json, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        else:
            raise ValueError(f"HTTP method {method} unsupported.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {str(e)}")
        # Return structured error with actual status code
        return {"code": e.response.status_code, "message": f"HTTP error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {"code": 500, "message": f"Request failed: {str(e)}"}
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return {"code": 400, "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"code": 500, "message": f"Unexpected error: {str(e)}"}