import requests

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, **kwargs):
    print(f"Invoking {method} request to {url}")
    if json:
        print(f"Payload: {json}")

    headers = {
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.43.3",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br"
    }

    try:
        if method.upper() not in SUPPORTED_HTTP_METHODS:
            raise Exception(f"HTTP method {method} unsupported.")

        response = requests.request(method, url, headers=headers, json=json, **kwargs)

        print(">>> Final URL:", response.url)
        print(">>> Status:", response.status_code)
        print(">>> Response:", response.text)

        try:
            result = response.json() if response.content else {}
        except Exception as e:
            return {
                "code": 500,
                "message": f"Invalid JSON output from service: {url}. {str(e)}"
            }

        result["code"] = response.status_code
        return result

    except Exception as e:
        return {
            "code": 500,
            "message": f"invocation of service fails: {url}. {str(e)}"
        }
