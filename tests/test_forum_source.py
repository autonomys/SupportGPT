import pytest
from supportgpt.sources.forum import ForumSource

from dotenv import load_dotenv
from os import getenv

load_dotenv()

src = ForumSource(getenv('FORUMS_API_KEY'), getenv('FORUMS_API_USERNAME'))


def test_categories():
    assert src.fetch_categories() != []
    assert "Support" in [cat['name'] for cat in src.fetch_categories()]

def test_topics():
    cats = { cat['name']: cat for cat in src.fetch_categories() }
    support = cats['Support']
    topics = src.fetch_topics(support['slug'], support['id'])
    assert "I think this bug" in [top['title'] for top in topics]

def test_posts():
    support  = { cat['name']: cat for cat in src.fetch_categories() }['Support']
    topic = { top['title']: top for top in src.fetch_topics(support['slug'], support['id']) }
    posts = src.fetch_posts(topic['I think this bug']['id'])

    assert any(post['accepted_answer'] for post in posts)
