import unittest

from omnity.core.catalog import Catalog
from omnity.ui.stream_resolver import (
    _select_playable_stream,
    requires_resolution,
)
from omnity.ui.subtitles import SubtitleTranslator


class StreamFeaturesTests(unittest.TestCase):
    def test_platform_links_are_resolved_without_false_domain_matches(self):
        self.assertTrue(requires_resolution("https://www.youtube.com/watch?v=abc"))
        self.assertTrue(requires_resolution("https://clips.twitch.tv/example"))
        self.assertTrue(requires_resolution("https://rumble.com/v123-example.html"))
        self.assertFalse(requires_resolution("https://youtube.com.example.org/video"))
        self.assertFalse(requires_resolution("https://example.org/live.m3u8"))

    def test_split_video_and_audio_formats_make_a_playable_stream(self):
        stream = _select_playable_stream(
            {
                "requested_formats": [
                    {
                        "url": "https://example.org/video.m3u8",
                        "vcodec": "h264",
                        "acodec": "none",
                        "http_headers": {"User-Agent": "test"},
                    },
                    {
                        "url": "https://example.org/audio.m3u8",
                        "vcodec": "none",
                        "acodec": "aac",
                    },
                ]
            }
        )
        self.assertEqual(stream["url"], "https://example.org/video.m3u8")
        self.assertEqual(stream["audio_url"], "https://example.org/audio.m3u8")
        self.assertEqual(stream["headers"], {"User-Agent": "test"})

    def test_single_stream_format_keeps_its_url(self):
        stream = _select_playable_stream(
            {
                "is_live": False,
                "url": "https://example.org/stream.m3u8",
                "http_headers": {"Referer": "https://example.org"},
            },
            max_video_height=720,
        )
        self.assertEqual(stream["url"], "https://example.org/stream.m3u8")
        self.assertIsNone(stream["audio_url"])
        self.assertEqual(stream["headers"], {"Referer": "https://example.org"})

    def test_live_stream_prefers_highest_video_format_within_height_cap(self):
        stream = _select_playable_stream(
            {
                "is_live": True,
                "url": "",
                "formats": [
                    {
                        "format_id": "720",
                        "url": "https://example.org/video-720.m3u8",
                        "height": 720,
                        "tbr": 2400,
                        "vcodec": "h264",
                        "acodec": "none",
                    },
                    {
                        "format_id": "1080",
                        "url": "https://example.org/video-1080.m3u8",
                        "height": 1080,
                        "tbr": 4500,
                        "vcodec": "h264",
                        "acodec": "none",
                    },
                    {
                        "format_id": "audio-low",
                        "url": "https://example.org/audio-low.m3u8",
                        "vcodec": "none",
                        "acodec": "aac",
                        "source_preference": 0,
                    },
                    {
                        "format_id": "audio-high",
                        "url": "https://example.org/audio-high.m3u8",
                        "vcodec": "none",
                        "acodec": "aac",
                        "source_preference": 1,
                    },
                ],
            },
            max_video_height=720,
        )
        self.assertEqual(stream["url"], "https://example.org/video-720.m3u8")
        self.assertEqual(stream["audio_url"], "https://example.org/audio-high.m3u8")

    def test_country_flag_is_derived_when_catalog_has_no_flag(self):
        catalog = Catalog()
        catalog.country_by_code = {"PL": {"name": "Poland"}}
        self.assertEqual(catalog.country_flag("PL"), "\U0001F1F5\U0001F1F1")
        self.assertEqual(catalog.country_flag("GLOBAL"), "")

    def test_google_translation_segments_are_joined(self):
        translated = SubtitleTranslator._parse_google(
            '[[["Cześć","Hello"],[" świecie"," world"]],null,"en"]'
        )
        self.assertEqual(translated, "Cześć świecie")


if __name__ == "__main__":
    unittest.main()
