import requests
from urllib.parse import urljoin
import jinja2

jinja_env = jinja2.Environment()


class ForumSource:
    TOPIC_TEMPLATE = jinja_env.from_string("""\
# {{ topic.title }}
{% for post in topic.posts %}
## Message from {{ post.author }}

```html
{{ post.content }}
```
{{ post.image_content }}
{% endfor %}
""")

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

    def _topics_raw(self, category_name):
        "Returns iterator over raw topics in category"
        cat = { cat['name']: cat for cat in self._fetch_categories() }[category_name]
        page = 0
        while True:
            topics = self._fetch_topics(cat['slug'], cat['id'], page=page)
            if len(topics) == 0:
                break
            page += 1
            for t in topics:
                yield t

    def _format_topic(self, topic_title, topic_id):
        "Returns markdown formatted topic"

        return self.TOPIC_TEMPLATE.render(topic={
            "title": topic_title,
            "posts": [
                {
                    "author": post["username"],
                    "content": post["cooked"],
                    # TODO: fetch image content
                    "image_content": "",
                }
                for post in self._fetch_posts(topic_id)
            ]
        })



    def _solved_topics(self, category_name):
        "Creates document from each solved topic in category"

        for topic in self._topics_raw(category_name):
            if not topic['has_accepted_answer']:
                continue

            yield self._format_topic(topic['title'], topic['id'])

