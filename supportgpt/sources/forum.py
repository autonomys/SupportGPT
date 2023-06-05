import requests
from urllib.parse import urljoin


class ForumSource:
    def __init__(self, api_key, api_username, base_url='https://forum.subspace.network'):
        self.api_key = api_key
        self.api_username = api_username
        self.base_url = base_url

    def _fetch(self, url, params=None):
        headers = { 'Api-Key': self.api_key, 'Api-Username': self.api_username }
        response = requests.get(urljoin(self.base_url, url), headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _fetch_categories(self):
        "Returns a list of categories"
        return self._fetch('/categories.json')['category_list']['categories']

    def _fetch_topics(self, category_slug, category_id, page=None):
        "Returns topics for a category"
        return self._fetch(f"/c/{category_slug}/{category_id}.json", params={ "page": page })['topic_list']['topics']

    def _fetch_posts(self, topic_id):
        "Returns posts for a topic"
        return self._fetch(f"/t/{topic_id}/posts.json")['post_stream']['posts']

    def _topics(self, category_name):
        "Returns iterator over topics in category"
        cat = { cat['name']: cat for cat in self._fetch_categories() }[category_name]
        page = 0
        while True:
            topics = self._fetch_topics(cat['slug'], cat['id'], page=page)
            if len(topics) == 0:
                break
            page += 1
            for t in topics:
                yield t


