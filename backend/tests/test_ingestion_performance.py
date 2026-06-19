from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base
from app.feed_utils import FetchResult
from app.models import ExternalSource, NormalizedItem
from app.services import run_ingestion


class IngestionPerformanceSettingsTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_article_enrichment_is_off_by_default(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GEOATLAS_ARTICLE_ENRICHMENT_ENABLED", None)
            get_settings.cache_clear()
            self.assertFalse(get_settings().article_enrichment_enabled)

    def test_ingestion_has_a_bounded_default_batch(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GEOATLAS_INGEST_MAX_NEW_ITEMS", None)
            get_settings.cache_clear()
            self.assertEqual(get_settings().ingest_max_new_items, 25)

    def test_external_geocoding_is_off_by_default(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GEOATLAS_EXTERNAL_GEOCODING_ENABLED", None)
            get_settings.cache_clear()
            self.assertFalse(get_settings().external_geocoding_enabled)


class BoundedIngestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        get_settings.cache_clear()
        self.engine.dispose()

    def test_default_ingest_stores_only_25_new_items_without_article_fetches(self) -> None:
        items = [
            {
                "id": f"item-{index}",
                "url": f"https://example.com/{index}",
                "title": f"Nigeria: Story {index}",
                "summary": "A short RSS summary.",
                "published_at": None,
                "image_url": None,
                "categories": [],
                "raw": {},
            }
            for index in range(100)
        ]
        parsed = {
            "feed_type": "rss",
            "title": "Example",
            "site_url": "https://example.com",
            "language": "en",
            "items": items,
        }
        fetched = FetchResult(
            url="https://example.com/feed",
            content_type="application/rss+xml",
            body=b"<rss />",
            etag=None,
            last_modified=None,
        )

        with Session(self.engine) as db:
            source = ExternalSource(name="Example", feed_url=fetched.url)
            db.add(source)
            db.commit()
            db.refresh(source)

            with (
                patch("app.services.safe_fetch", return_value=fetched),
                patch("app.services.parse_feed_bytes", return_value=parsed),
                patch("app.services.extract_article") as article_fetch,
            ):
                job = run_ingestion(db, source)

            stored = db.scalar(select(func.count()).select_from(NormalizedItem))
            self.assertEqual(job.normalized_count, 25)
            self.assertEqual(stored, 25)
            article_fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
