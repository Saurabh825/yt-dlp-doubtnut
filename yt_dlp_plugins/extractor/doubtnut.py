# ⚠ Don't use relative imports
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils.traversal import traverse_obj

# ℹ️ If you need to import from another plugin
# from yt_dlp_plugins.extractor.example import ExamplePluginIE

# ℹ️ Instructions on making extractors can be found at:
# 🔗 https://github.com/yt-dlp/yt-dlp/blob/master/CONTRIBUTING.md#adding-support-for-a-new-site


# ⚠ The class name must end in "IE"
class DoubtnutIE(InfoExtractor):
    # _WORKING = False
    _VALID_URL = r"https?://(?:www\.)?doubtnut\.com/qna/(?P<id>\d+)"

    _TESTS = [
        {
            "url": "https://www.doubtnut.com/qna/6738",
            "info_dict": {
                "id": "6738",
                "title": "Example video",
                "ext": "mp4",
            },
        }
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # Extract the __NEXT_DATA__ JSON blob from the webpage
        next_data_json = self._search_regex(
            r'<script\s+id="__NEXT_DATA__"\s+type="application/json"[^>]*>\s*({.+?})\s*</script>',
            webpage,
            "next data",
            default=None,
        )

        if not next_data_json:
            self.report_warning("Could not extract __NEXT_DATA__ from the webpage.")
            return

        next_data = self._parse_json(next_data_json, video_id, fatal=False)
        if not next_data:
            return

        # Use traverse_obj to safely and concisely extract video data
        video_data = traverse_obj(next_data, ("props", "pageProps", "videoData"))
        if not video_data:
            self.report_warning("Could not extract video data from JSON.")
            return

        # Extract the video filename
        video_name = traverse_obj(video_data, "video_name")
        if not video_name:
            self.report_warning("Could not find video filename in the JSON data.")
            return

        # Use traverse_obj to get metadata, providing fallbacks for the title
        title = traverse_obj(video_data, "title") or traverse_obj(
            next_data, ("props", "pageProps"), "ocrText"
        )

        return {
            "id": video_id,
            "title": title,
            "url": f"https://videos.doubtnut.com/{video_name}",
            "thumbnail": traverse_obj(video_data, "answer_image_url"),
            "duration": int(traverse_obj(video_data, "duration")),
        }
