import requests
import jinja2
import cv2
import numpy as np

from urllib.parse import urljoin
from pytesseract import image_to_string


jinja_env = jinja2.Environment()


def is_url_image(url):
    response = requests.head(url)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type', '').lower()
    return content_type.startswith('image/')

def url_image_to_text(url):
    if not is_url_image(url):
        return None

    # Download the image
    response = requests.get(url)
    if response.status_code != 200:
        return None

    # Convert the image data to OpenCV format
    image_data = np.frombuffer(response.content, dtype=np.uint8)
    img = cv2.imdecode(image_data, flags=cv2.IMREAD_COLOR)

    # Convert the image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply OCR
    return image_to_string(gray_img)


class ForumSource:
    TOPIC_TEMPLATE = jinja_env.from_string("""\
# {{ topic.title }}
{% for post in topic.posts %}
## Message from {{ post.author }}

```html
{{ post.content }}
```

Image content:
```
{% for image in post.images %}
{{ image }}
{% endfor %}
```

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

        posts = []

        for post in self._fetch_posts(topic_id):
            images = []

            if "link_counts" in post:
                for link in post["link_counts"]:
                    if link["url"].startswith("http"):
                        images.append(url_image_to_text(link["url"]))

            if "image_url" in post:
                images.append(url_image_to_text(post["image_url"]))

            posts.append({
                "author": post["username"],
                "content": post["cooked"],
                "images": images,
            })

        return self.TOPIC_TEMPLATE.render(topic={ "title": topic_title, "posts": posts })



    def _solved_topics(self, category_name):
        "Creates document from each solved topic in category"

        for topic in self._topics_raw(category_name):
            if not topic['has_accepted_answer']:
                continue

            yield self._format_topic(topic['title'], topic['id'])

