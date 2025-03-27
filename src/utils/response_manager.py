import requests
from fastapi import HTTPException


def check_for_error(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(response.json())
        raise HTTPException(status_code=response.status_code, detail=str(e))
