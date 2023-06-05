import pytest
from supportgpt.sources.forum import ForumSource

from dotenv import load_dotenv
from os import getenv

load_dotenv()

src = ForumSource(getenv('FORUMS_API_KEY'), getenv('FORUMS_API_USERNAME'))


def test_categories():
    assert src.fetch_categories() != []
    assert "Support" in [cat['name'] for cat in src.fetch_categories()]

