"""
Django management command to scrape YouTube video transcripts.

Usage examples:
    python manage.py scrape_youtube --channel-id UCakddO7wKR9RAdK0VYlJ4Vw  # Ryan Reeves
    python manage.py scrape_youtube --playlist-id PLfp-ewnzgGDPYFPALnxYY8kWuqL0XdsQn
    python manage.py scrape_youtube --video-id dQw4w9WgXcQ
    python manage.py scrape_youtube --channel-id xxx --dry-run
"""

import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.content.models import ContentItem, Source


class Command(BaseCommand):
    """Scrape YouTube video transcripts and store in database."""

    help = "Scrape YouTube video transcripts from channels, playlists, or individual videos"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--channel-id",
            type=str,
            help="YouTube channel ID to scrape",
        )
        parser.add_argument(
            "--playlist-id",
            type=str,
            help="YouTube playlist ID to scrape",
        )
        parser.add_argument(
            "--video-id",
            type=str,
            help="Single YouTube video ID to scrape",
        )
        parser.add_argument(
            "--source-name",
            type=str,
            help="Name for the Source record (defaults to channel/playlist name)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List videos without scraping transcripts",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of videos to scrape (0 = no limit)",
        )
        parser.add_argument(
            "--language",
            type=str,
            default="en",
            help="Preferred transcript language (default: en)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        channel_id = options["channel_id"]
        playlist_id = options["playlist_id"]
        video_id = options["video_id"]
        source_name = options["source_name"]
        dry_run = options["dry_run"]
        limit = options["limit"]
        language = options["language"]

        # Validate arguments
        if not any([channel_id, playlist_id, video_id]):
            raise CommandError(
                "Must specify one of: --channel-id, --playlist-id, or --video-id"
            )

        if sum(bool(x) for x in [channel_id, playlist_id, video_id]) > 1:
            raise CommandError(
                "Cannot specify more than one of: --channel-id, --playlist-id, --video-id"
            )

        try:
            # Get list of video IDs to process
            if channel_id:
                self.stdout.write(f"Fetching videos from channel: {channel_id}")
                video_ids = self._get_channel_videos(channel_id, limit)
                source_type = Source.SourceType.YOUTUBE_CHANNEL
                source_url = f"https://www.youtube.com/channel/{channel_id}"
            elif playlist_id:
                self.stdout.write(f"Fetching videos from playlist: {playlist_id}")
                video_ids = self._get_playlist_videos(playlist_id, limit)
                source_type = Source.SourceType.YOUTUBE_PLAYLIST
                source_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            else:  # video_id
                self.stdout.write(f"Processing single video: {video_id}")
                video_ids = [video_id]
                source_type = Source.SourceType.YOUTUBE_CHANNEL
                source_url = f"https://www.youtube.com/watch?v={video_id}"

            if not video_ids:
                self.stdout.write(self.style.WARNING("No videos found"))
                return

            self.stdout.write(f"Found {len(video_ids)} video(s)")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No transcripts will be scraped"))
                for vid in video_ids:
                    self.stdout.write(f"  - https://www.youtube.com/watch?v={vid}")
                return

            # Get or create source
            if not source_name and channel_id:
                source_name = self._get_channel_name(channel_id) or f"YouTube Channel {channel_id}"
            elif not source_name and playlist_id:
                source_name = f"YouTube Playlist {playlist_id}"
            elif not source_name:
                source_name = f"YouTube Video {video_id}"

            source, created = Source.objects.get_or_create(
                url=source_url,
                defaults={
                    "name": source_name,
                    "source_type": source_type,
                    "scrape_config": {"language": language},
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created source: {source.name}"))
            else:
                self.stdout.write(f"Using existing source: {source.name}")

            # Scrape transcripts
            stats = {"scraped": 0, "skipped": 0, "failed": 0}

            for idx, vid in enumerate(video_ids, 1):
                self.stdout.write(f"\n[{idx}/{len(video_ids)}] Processing video: {vid}")

                # Check if already exists
                if ContentItem.objects.filter(source=source, external_id=vid).exists():
                    self.stdout.write(self.style.WARNING(f"  Skipped - already in database"))
                    stats["skipped"] += 1
                    continue

                try:
                    # Scrape transcript
                    content_item = self._scrape_video(source, vid, language)
                    if content_item:
                        self.stdout.write(self.style.SUCCESS(f"  Scraped: {content_item.title}"))
                        stats["scraped"] += 1
                    else:
                        stats["skipped"] += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Failed: {str(e)}"))
                    stats["failed"] += 1

                # Rate limiting
                if idx < len(video_ids):
                    time.sleep(2)

            # Print summary
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS(f"Scraped: {stats['scraped']}"))
            self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']}"))
            if stats["failed"] > 0:
                self.stdout.write(self.style.ERROR(f"Failed: {stats['failed']}"))
            self.stdout.write("=" * 50)

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\n\nInterrupted by user"))
            raise CommandError("Command interrupted")

    def _get_channel_videos(self, channel_id: str, limit: int = 0) -> List[str]:
        """Get video IDs from a YouTube channel via RSS feed."""
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

        video_ids = []
        for entry in root.findall("atom:entry", ns):
            video_id = entry.find("yt:videoId", ns)
            if video_id is not None and video_id.text:
                video_ids.append(video_id.text)
                if limit > 0 and len(video_ids) >= limit:
                    break

        return video_ids

    def _get_playlist_videos(self, playlist_id: str, limit: int = 0) -> List[str]:
        """Get video IDs from a YouTube playlist via RSS feed."""
        url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

        video_ids = []
        for entry in root.findall("atom:entry", ns):
            video_id = entry.find("yt:videoId", ns)
            if video_id is not None and video_id.text:
                video_ids.append(video_id.text)
                if limit > 0 and len(video_ids) >= limit:
                    break

        return video_ids

    def _get_channel_name(self, channel_id: str) -> Optional[str]:
        """Get channel name from RSS feed."""
        try:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            title = root.find("atom:title", ns)
            return title.text if title is not None else None
        except Exception:
            return None

    def _scrape_video(
        self, source: Source, video_id: str, language: str
    ) -> Optional[ContentItem]:
        """Scrape transcript for a single video."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            raise CommandError(
                "youtube-transcript-api is not installed. "
                "Install it with: pip install youtube-transcript-api"
            )

        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try to get preferred language, fall back to auto-generated
            try:
                transcript = transcript_list.find_transcript([language])
            except Exception:
                # Get any available transcript
                transcript = transcript_list.find_generated_transcript([language])

            transcript_data = transcript.fetch()

            # Combine transcript segments
            raw_text = "\n".join(segment["text"] for segment in transcript_data)

            # Get video metadata via oembed API (no auth required)
            metadata = self._get_video_metadata(video_id)

            # Create ContentItem
            content_item = ContentItem.objects.create(
                source=source,
                content_type=ContentItem.ContentType.TRANSCRIPT,
                title=metadata.get("title", f"YouTube Video {video_id}"),
                url=f"https://www.youtube.com/watch?v={video_id}",
                external_id=video_id,
                author=metadata.get("author_name", ""),
                raw_text=raw_text,
                metadata={
                    "language": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable,
                    **metadata,
                },
            )

            return content_item

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  No transcript available: {str(e)}"))
            return None

    def _get_video_metadata(self, video_id: str) -> dict:
        """Get video metadata via oEmbed API (no auth required)."""
        try:
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}
