import requests
from urllib.parse import urljoin


class ForumSource:
    def __init__(self, api_key, api_username, base_url='https://forum.subspace.network'):
        self.api_key = api_key
        self.api_username = api_username
        self.base_url = base_url

    def _fetch(self, url):
        headers = { 'Api-Key': self.api_key, 'Api-Username': self.api_username }
        response = requests.get(urljoin(self.base_url, url), headers=headers)
        response.raise_for_status()
        return response.json()

    def fetch_categories(self):
        "Returns a list of categories"
        return self._fetch('/categories.json')['category_list']['categories']

