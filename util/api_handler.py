"""
    This file will have the code for the API handler
"""

# IMPORTS ==========================================================
import json

import httpx


# CLASSES ==========================================================
class APIHandler:
    """ Class made to handle external API requests """
    def __init__(self, base_url):
        self.base_url = base_url

    def get_data(self, endpoint):
        """ This is where we make the GET request """
        try:
            # try to make the GET request
            response = httpx.get(f'{self.base_url}/{endpoint}')
            if response.status_code != 200:
                return {
                    'error': 'Bad request!',
                    'code': response.status_code
                }
            return {
                'response': json.loads(response.text),
                'code': 200
            }
        except ImportError:
            print('GET request to external API failed')
            return {
                'error': 'GET request to external API failed',
                'code': 500
            }
