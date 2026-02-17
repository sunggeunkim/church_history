"""
Django management command to scrape web content from articles and blogs.

Usage examples:
    python manage.py scrape_web --url "https://www.ligonier.org/learn/articles/" --source-name "Ligonier"
    python manage.py scrape_web --sitemap "https://example.com/sitemap.xml" --source-name "Blog"
    python manage.py scrape_web --url-file urls.txt --source-name "Custom"
    python manage.py scrape_web --url "..." --dry-run
"""

import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from django.core.management.base import BaseCommand, CommandError

from apps.content.models import ContentItem, Source


class Command(BaseCommand):
    """Scrape web content from articles and blogs."""

    help = "Scrape web content from articles, blogs, and websites"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--url",
            type=str,
            help="Single URL to scrape",
        )
        parser.add_argument(
            "--sitemap",
            type=str,
            help="XML sitemap URL to scrape all articles from",
        )
        parser.add_argument(
            "--url-file",
            type=str,
            help="Path to file containing URLs (one per line)",
        )
        parser.add_argument(
            "--source-name",
            type=str,
            required=True,
            help="Name for the Source record",
        )
        parser.add_argument(
            "--follow-links",
            action="store_true",
            help="Discover and follow article links from index page",
        )
        parser.add_argument(
            "--max-depth",
            type=int,
            default=1,
            help="Maximum depth for link following (default: 1)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List URLs without scraping content",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of articles to scrape (0 = no limit)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        url = options["url"]
        sitemap = options["sitemap"]
        url_file = options["url_file"]
        source_name = options["source_name"]
        follow_links = options["follow_links"]
        max_depth = options["max_depth"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        # Validate arguments
        if not any([url, sitemap, url_file]):
            raise CommandError("Must specify one of: --url, --sitemap, or --url-file")

        if sum(bool(x) for x in [url, sitemap, url_file]) > 1:
            raise CommandError("Cannot specify more than one of: --url, --sitemap, --url-file")

        try:
            # Get list of URLs to process
            if url:
                if follow_links:
                    self.stdout.write(f"Discovering links from: {url}")
                    urls = self._discover_links(url, max_depth, limit)
                else:
                    urls = [url]
            elif sitemap:
                self.stdout.write(f"Fetching URLs from sitemap: {sitemap}")
                urls = self._get_sitemap_urls(sitemap, limit)
            else:  # url_file
                self.stdout.write(f"Reading URLs from file: {url_file}")
                urls = self._read_url_file(url_file, limit)

            if not urls:
                self.stdout.write(self.style.WARNING("No URLs found"))
                return

            self.stdout.write(f"Found {len(urls)} URL(s)")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No content will be scraped"))
                for u in urls:
                    self.stdout.write(f"  - {u}")
                return

            # Get or create source
            # Use first URL or sitemap URL as source URL
            source_url = sitemap or url or urls[0]

            source, created = Source.objects.get_or_create(
                url=source_url,
                defaults={
                    "name": source_name,
                    "source_type": Source.SourceType.WEBSITE,
                    "scrape_config": {},
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created source: {source.name}"))
            else:
                self.stdout.write(f"Using existing source: {source.name}")

            # Check robots.txt
            base_url = self._get_base_url(source_url)
            robots_parser = self._get_robots_parser(base_url)

            # Scrape articles
            stats = {"scraped": 0, "skipped": 0, "failed": 0}

            for idx, article_url in enumerate(urls, 1):
                self.stdout.write(f"\n[{idx}/{len(urls)}] Processing: {article_url}")

                # Check robots.txt
                if robots_parser and not robots_parser.can_fetch("*", article_url):
                    self.stdout.write(self.style.WARNING(f"  Skipped - blocked by robots.txt"))
                    stats["skipped"] += 1
                    continue

                # Check if already exists
                if ContentItem.objects.filter(source=source, url=article_url).exists():
                    self.stdout.write(self.style.WARNING(f"  Skipped - already in database"))
                    stats["skipped"] += 1
                    continue

                try:
                    # Scrape article
                    content_item = self._scrape_article(source, article_url)
                    if content_item:
                        self.stdout.write(self.style.SUCCESS(f"  Scraped: {content_item.title}"))
                        stats["scraped"] += 1
                    else:
                        stats["skipped"] += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Failed: {str(e)}"))
                    stats["failed"] += 1

                # Rate limiting
                if idx < len(urls):
                    time.sleep(3)

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

    def _get_sitemap_urls(self, sitemap_url: str, limit: int = 0) -> List[str]:
        """Get URLs from XML sitemap."""
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        urls = []
        for url_element in root.findall(".//sm:url/sm:loc", ns):
            if url_element.text:
                urls.append(url_element.text)
                if limit > 0 and len(urls) >= limit:
                    break

        return urls

    def _read_url_file(self, file_path: str, limit: int = 0) -> List[str]:
        """Read URLs from a text file."""
        urls = []
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
                    if limit > 0 and len(urls) >= limit:
                        break
        return urls

    def _discover_links(self, start_url: str, max_depth: int, limit: int = 0) -> List[str]:
        """Discover article links from an index page."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise CommandError(
                "beautifulsoup4 is not installed. "
                "Install it with: pip install beautifulsoup4"
            )

        discovered = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        visited = set()

        while to_visit and (limit == 0 or len(discovered) < limit):
            current_url, depth = to_visit.pop(0)

            if current_url in visited or depth > max_depth:
                continue

            visited.add(current_url)

            try:
                response = requests.get(current_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)

                    # Only include links from same domain
                    if self._same_domain(start_url, absolute_url):
                        discovered.add(absolute_url)

                        # Add to visit queue if within depth limit
                        if depth < max_depth:
                            to_visit.append((absolute_url, depth + 1))

                        if limit > 0 and len(discovered) >= limit:
                            break

                time.sleep(2)  # Rate limiting

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to discover links from {current_url}: {str(e)}"))

        return list(discovered)

    def _scrape_article(self, source: Source, url: str) -> Optional[ContentItem]:
        """Scrape a single article."""
        try:
            import trafilatura
        except ImportError:
            raise CommandError(
                "trafilatura is not installed. "
                "Install it with: pip install trafilatura"
            )

        try:
            # Download and extract article
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                self.stdout.write(self.style.WARNING(f"  Failed to download content"))
                return None

            # Extract with metadata
            result = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                output_format='txt',
                with_metadata=True,
            )

            if not result:
                self.stdout.write(self.style.WARNING(f"  No content extracted"))
                return None

            # Parse metadata
            metadata = trafilatura.extract_metadata(downloaded)

            title = metadata.title if metadata and metadata.title else url
            author = metadata.author if metadata and metadata.author else ""
            published_date = None

            if metadata and metadata.date:
                try:
                    # Parse date (trafilatura returns ISO format)
                    published_date = datetime.fromisoformat(metadata.date.replace('Z', '+00:00')).date()
                except Exception:
                    pass

            # Create ContentItem
            content_item = ContentItem.objects.create(
                source=source,
                content_type=ContentItem.ContentType.ARTICLE,
                title=title,
                url=url,
                author=author,
                published_date=published_date,
                raw_text=result,
                metadata={
                    "description": metadata.description if metadata and metadata.description else "",
                    "sitename": metadata.sitename if metadata and metadata.sitename else "",
                    "categories": metadata.categories if metadata and metadata.categories else [],
                    "tags": metadata.tags if metadata and metadata.tags else [],
                },
            )

            return content_item

        except Exception as e:
            raise Exception(f"Scraping failed: {str(e)}")

    def _get_base_url(self, url: str) -> str:
        """Get base URL (scheme + netloc)."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain."""
        return urlparse(url1).netloc == urlparse(url2).netloc

    def _get_robots_parser(self, base_url: str) -> Optional[RobotFileParser]:
        """Get robots.txt parser for a domain."""
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()
            return parser
        except Exception:
            # If robots.txt doesn't exist or can't be read, allow all
            return None
