from __future__ import annotations
from typing import Any, Dict
import requests
import json

def post_file(data: Any, request_id: str, ) -> int:
    ''' Sends a request to a server. '''
    response = requests.post(request_id, json=data.dict())
    return response.status_code

def get_response_code(request_id: str, ) -> int:
    ''' Sends a request to a server. '''
    response = requests.get(request_id)
    return response.status_code

def get_response(request_id: str) -> Dict:
    """ Gets the response from a server. """
    data = requests.get(request_id)
    return json.loads(data.text)
