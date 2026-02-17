# P2: Content Scraping Pipeline — Comprehensive Research

**Research Date:** February 16, 2026
**Researcher:** AI Agent Team
**Purpose:** Technical research for Toledot content scraping pipeline in the Reformed tradition

---

## Table of Contents
1. [YouTube Transcript Scraping](#1-youtube-transcript-scraping)
2. [Web Scraping Libraries](#2-web-scraping-libraries)
3. [Target Content Sources](#3-target-content-sources)
4. [Text Processing for RAG](#4-text-processing-for-rag)
5. [Embedding Models](#5-embedding-models)
6. [pgvector Configuration](#6-pgvector-configuration)
7. [Legal & Ethical Considerations](#7-legal--ethical-considerations)
8. [Dependencies to Add](#8-dependencies-to-add)
9. [Architecture Decision Summary](#9-architecture-decision-summary)

---

## 1. YouTube Transcript Scraping

### `youtube-transcript-api`

**License:** MIT ✅
**Latest Version:** 1.2.4 (January 29, 2026)
**Python Compatibility:** Python ≥3.8 and <3.15
**PyPI:** [pypi.org/project/youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/)
**GitHub:** [github.com/jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

**How it works:**
- Retrieves transcripts/subtitles for YouTube videos without requiring an API key
- Works with both manual and automatically generated subtitles
- Supports subtitle translation
- Uses direct HTTP requests (no headless browser or Selenium needed)
- No YouTube Data API quota consumption

**Installation:**
```bash
pip install youtube-transcript-api
```

**Basic Usage:**
```python
from youtube_transcript_api import YouTubeTranscriptApi

# Get transcript for a single video
transcript = YouTubeTranscriptApi.get_transcript('video_id')

# Returns list of dicts: [{'text': '...', 'start': 0.0, 'duration': 2.5}, ...]
```

**Pros:**
- Completely free, no API key required
- MIT license (commercial-friendly)
- Actively maintained (latest release Jan 2026)
- Simple Python API
- Supports translation

**Cons:**
- Only fetches transcripts (does not download video/audio)
- Dependent on YouTube's caption system
- May break if YouTube changes internal APIs
- No built-in rate limiting (must implement manually)

**Recommendation:** **Use `youtube-transcript-api`** as primary transcript extraction tool. It's sufficient for our needs and avoids YouTube Data API quota issues.

---

### `yt-dlp`

**License:** Unlicense (Public Domain) ✅
**Latest Version:** 2026.02.04 (February 4, 2026)
**PyPI:** [pypi.org/project/yt-dlp](https://pypi.org/project/yt-dlp/)
**GitHub:** [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)

**What it is:**
- Fork of `youtube-dl` with active maintenance and improvements
- Command-line tool and Python library for downloading videos from YouTube and 1000+ sites
- Can extract metadata, transcripts, thumbnails, and more without downloading video

**Key capabilities:**
- List all videos from a channel or playlist (without downloading)
- Extract video metadata (title, description, upload date, etc.)
- Get transcript/subtitle files
- Download full videos/audio (if needed)

**Dependency licenses:**
- **yt-dlp-ejs:** Unlicense (required for full YouTube support)
- **certifi:** MPLv2
- **brotli/brotlicffi:** MIT
- **requests:** Apache-2.0
- **pycryptodomex:** BSD-2-Clause

**Installation:**
```bash
pip install yt-dlp
```

**Getting channel/playlist videos (Python API):**
```python
import yt_dlp

ydl_opts = {
    'extract_flat': True,   # Don't download, just list
    'quiet': True,
}

channel_url = "https://www.youtube.com/@SomeChannel/videos"

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(channel_url, download=False)
    for entry in info['entries']:
        print(entry['id'], entry['title'])
```

**Recommendation:** **Use `yt-dlp`** for:
- Getting video lists from channels/playlists (no YouTube Data API needed)
- Extracting rich metadata
- Backup transcript extraction if `youtube-transcript-api` fails

**Not needed for:** Basic transcript-only extraction (use `youtube-transcript-api` instead)

---

### YouTube RSS Feeds for Video Discovery

**No API key required.** YouTube exposes RSS feeds for channels and playlists that return the 15 most recent videos.

**Channel RSS feed format:**
```
https://www.youtube.com/feeds/videos.xml?channel_id=UCakddO7wKR9RAdK0VYlJ4Vw
```

**Playlist RSS feed format:**
```
https://www.youtube.com/feeds/videos.xml?playlist_id=PLRgREWf4NFWZEd86aVEpQ7B3YxXPhUEf-
```

**Parsing RSS feeds:**
```python
import feedparser

def get_channel_videos_rss(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)
    return [
        {
            'video_id': entry.yt_videoid,
            'title': entry.title,
            'published': entry.published,
            'url': entry.link,
        }
        for entry in feed.entries
    ]

# Ryan Reeves channel
videos = get_channel_videos_rss("UCakddO7wKR9RAdK0VYlJ4Vw")
```

**Limitations:**
- Returns only the 15 most recent videos (not full history)
- For full channel history, use yt-dlp or YouTube Data API

**Use case:** Polling for new content (scheduled scraping), not initial bulk import.

---

### YouTube oEmbed API for Video Metadata

**No API key required.** Returns title, author, thumbnail, and embed HTML for any public video.

**Endpoint:**
```
https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json
```

**Usage:**
```python
import requests

def get_video_metadata_oembed(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
    # Returns: {'title': '...', 'author_name': '...', 'author_url': '...', 'thumbnail_url': '...', ...}
```

**Limitations:**
- Does not return upload date, description, or view count
- Only works for public, embeddable videos

**Use case:** Lightweight metadata enrichment without API quota costs.

---

### Getting Channel/Playlist Videos Without YouTube Data API

**Why avoid the API?**
- YouTube Data API has a daily quota of only **10,000 units/day**
- A single channel video list request can consume 100 units
- Impractical for large-scale scraping

**Solution 1: yt-dlp (Recommended for bulk import)**
```python
import yt_dlp

def get_channel_videos(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return [(entry['id'], entry['title']) for entry in info['entries']]

# Example
videos = get_channel_videos("https://www.youtube.com/@RyanReevesFilms/videos")
```

**Solution 2: youtube-search-python**
- Library: `youtube-search-python`
- License: MIT ✅
- Simulates YouTube's web client requests
- Good for searching and metadata retrieval

```bash
pip install youtube-search-python
```

**Recommendation:** **Use yt-dlp** for channel/playlist enumeration. It's more reliable and battle-tested.

---

### Rate Limiting Best Practices for YouTube

**YouTube's perspective:**
- YouTube allows transcript access for educational purposes
- No explicit rate limits documented, but excessive requests trigger blocking
- robots.txt allows crawling but expects reasonable behavior

**Recommended practices:**
1. **Respect Crawl-Delay:** Add 1-2 second delays between requests
2. **Implement exponential backoff:** On errors, wait progressively longer
3. **Use a User-Agent:** Identify your scraper honestly
4. **Avoid parallel requests:** Stick to sequential processing
5. **Scrape during off-peak hours:** Minimize server impact
6. **Cache aggressively:** Never re-fetch the same transcript

**Implementation:**
```python
import time
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript_with_retry(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            time.sleep(2)  # 2-second delay
            return YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

**Monitoring:**
- Track HTTP 429 (Too Many Requests) responses
- Log request timing and failures
- Adjust delays based on error rates

---

## 2. Web Scraping Libraries

### Recommended Libraries (All Permissive Licenses)

| Library | License | Purpose | Version | Status |
|---------|---------|---------|---------|--------|
| `trafilatura` | Apache-2.0 ✅ | Article extraction | 2.0.0 | **Recommended** |
| `beautifulsoup4` | MIT ✅ | HTML parsing | Latest | Utility |
| `newspaper4k` | MIT ✅ | News article extraction | Latest | Alternative |
| `requests` | Apache-2.0 ✅ | HTTP client | Latest | Already in use |
| `lxml` | BSD ✅ | XML/HTML parser | Latest | Utility |

---

### `trafilatura` (PRIMARY RECOMMENDATION)

**License:** Apache-2.0 ✅ (GPLv3+ for versions < 1.8.0)
**Latest Version:** 2.0.0
**PyPI:** [pypi.org/project/trafilatura](https://pypi.org/project/trafilatura/)
**GitHub:** [github.com/adbar/trafilatura](https://github.com/adbar/trafilatura)
**Docs:** [trafilatura.readthedocs.io](https://trafilatura.readthedocs.io/)

**What makes it excellent:**
- **#1 ranked** in ScrapingHub's article extraction benchmark
- Designed specifically for extracting main text content from web pages
- Removes boilerplate (headers, footers, ads, navigation)
- Extracts metadata (title, author, publish date)
- Supports multiple output formats: JSON, XML, Markdown, Plain Text, HTML, XML-TEI
- Built-in duplicate detection
- Language detection
- Actively maintained by academic researchers (PhD-level NLP expertise)

**Why it's perfect for church history content:**
- Excellent at extracting article body text from complex layouts
- Preserves semantic structure (paragraphs, lists, headings)
- Handles long-form theological articles well
- Used by HuggingFace, IBM, Microsoft Research

**Installation:**
```bash
pip install trafilatura
```

**Basic usage:**
```python
import trafilatura

# Download and extract
downloaded = trafilatura.fetch_url('https://www.ligonier.org/some-article')
text = trafilatura.extract(downloaded)

# With metadata
result = trafilatura.extract(downloaded, output_format='json', include_comments=False)
# Returns: {'title': '...', 'author': '...', 'date': '...', 'text': '...'}
```

**Recommendation:** **Use trafilatura as primary web scraping tool** for all Reformed content sources (Ligonier, TGC, Monergism, etc.). It balances quality, speed, and ease of use.

---

### `newspaper4k` (Alternative)

**License:** MIT ✅
**PyPI:** [pypi.org/project/newspaper4k](https://pypi.org/project/newspaper4k/)
**GitHub:** [github.com/AndyTheFactory/newspaper4k](https://github.com/AndyTheFactory/newspaper4k)

**Background:**
- Fork of the original `newspaper3k` (abandoned in 2020)
- Actively maintained by Andrei Paraschiv
- Minimum Python version: 3.10

**Features:**
- Multi-language support (40+ languages)
- Article extraction, metadata, images
- Built-in NLP (summarization, keyword extraction)
- News source parsing

**When to use:**
- If you need NLP features (summarization, keywords)
- If you need image extraction
- If you need multi-language support beyond English

**Recommendation:** **Use as backup** if trafilatura fails on specific sites. Trafilatura is generally more accurate for article body extraction.

---

### `beautifulsoup4`

**License:** MIT ✅
**PyPI:** [pypi.org/project/beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

**Purpose:**
- Low-level HTML/XML parsing
- Custom extraction logic when automated tools fail
- Handling non-standard page structures

**When to use:**
- For sites that trafilatura can't handle
- For extracting specific DOM elements (e.g., sermon series metadata)
- For debugging extraction issues

**Installation:**
```bash
pip install beautifulsoup4 lxml
```

---

### Scraping Best Practices

#### robots.txt Compliance

**Always check robots.txt before scraping:**
```python
import urllib.robotparser

def can_scrape(url):
    rp = urllib.robotparser.RobotFileParser()
    base_url = '/'.join(url.split('/')[:3])
    rp.set_url(f"{base_url}/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)
```

**Key points:**
- Recheck robots.txt daily (policies change)
- Respect `Disallow` directives
- Honor `Crawl-delay` if specified
- Use `reppy` library for production (faster, supports caching)

#### Rate Limiting

**Implementation:**
```python
import time
import random

def fetch_with_rate_limit(url):
    time.sleep(random.uniform(1.5, 3.0))  # Random delay 1.5-3s
    return trafilatura.fetch_url(url)
```

**Guidelines:**
- **Small sites:** 2-5 second delays between requests
- **Large sites:** 1-2 second delays
- **Off-peak hours:** Scrape during nighttime in site's timezone
- **Monitor HTTP 429:** Implement exponential backoff on rate limit errors

#### User-Agent

**Set an honest, identifiable User-Agent:**
```python
import trafilatura

config = trafilatura.settings.use_config()
config.set("DEFAULT", "USER_AGENTS", "ToledotBot/1.0 (Reformed Church History Educational App; contact@toledot.app)")

downloaded = trafilatura.fetch_url(url, config=config)
```

---

## 3. Target Content Sources for Reformed Church History

### 1. Ryan Reeves YouTube Channel

**Channel:** [@RyanReevesFilms](https://www.youtube.com/@RyanReevesFilms)
**Channel ID:** `UCakddO7wKR9RAdK0VYlJ4Vw`
**About:** Dr. Ryan Reeves, Associate Professor of Historical Theology at Gordon-Conwell Theological Seminary
**Content:** Church history lectures covering Ancient, Medieval, Reformation, and Modern periods
**License/Permission:** Public educational content, transcripts via YouTube

**Key Playlists:**

| Playlist | URL | Description | Videos |
|----------|-----|-------------|--------|
| Early & Medieval Church | `https://www.youtube.com/playlist?list=PLRgREWf4NFWZEd86aVEpQ7B3YxXPhUEf-` | ~55 lectures on early church history | ~55 |
| Reformation & Modern Church | `https://www.youtube.com/playlist?list=PLRgREWf4NFWY1ZaP-falnLFIR9texgvjR` | Luther, Calvin, Puritans, Awakenings | ~60+ |
| Tolkien and Lewis | Available | Christian authors and theology | ~10+ |
| Luther and Calvin | Available | Reformers deep dive | ~15+ |

**Topics covered:**
- Late Medieval background to Reformation
- Luther's Reformation breakthrough
- Calvin, Bullinger, Zwingli
- Puritans, Westminster Assembly
- Enlightenment and church response
- John Wesley, Jonathan Edwards
- Great Awakenings
- Modern church movements

**Scraping strategy:**
1. Use `yt-dlp` to get all video IDs from playlists
2. Use `youtube-transcript-api` to fetch transcripts
3. Store video metadata (title, upload date, playlist)
4. Chunk transcripts by natural speaking boundaries (see Section 4)

**Estimated content:** ~100+ videos × 30 minutes average = ~50 hours of lecture content

---

### 2. Ligonier Ministries

**URL:** [ligonier.org](https://www.ligonier.org/)
**About:** R.C. Sproul's teaching ministry, leading Reformed resource provider
**Content:** Articles, Tabletalk magazine, teaching series, devotionals

**Copyright Policy Summary:**
- **Non-commercial reproduction allowed:** Up to 500 physical copies
- **Attribution required:** Must cite "Tabletalk magazine of Ligonier Ministries" with hyperlink
- **No alterations:** Content must not be modified
- **Commercial use:** Requires written permission
- **Book excerpts:** Up to 250 words allowed with citation

**Scraping recommendation:**
- **Articles:** Fully scrapable with proper attribution
- **Tabletalk magazine:** Requires attribution with hyperlink to TabletalkMagazine.com
- **Books:** Limited to 250-word excerpts only

**Key resources:**
- R.C. Sproul teaching archives
- Tabletalk magazine (reaching 260,000+ readers monthly)
- Ligonier.org article library
- Reformed theology explainers

**Technical approach:**
```python
import trafilatura

url = "https://www.ligonier.org/learn/articles/some-article"
downloaded = trafilatura.fetch_url(url)
data = trafilatura.extract(downloaded, output_format='json')

# Store with attribution
metadata = {
    'source': 'Ligonier Ministries',
    'attribution': 'Tabletalk magazine of Ligonier Ministries',
    'url': url,
    'title': data['title'],
    'author': data['author'],
    'date': data['date'],
    'content': data['text']
}
```

**Legal compliance:**
- Store attribution in database
- Display attribution in UI when showing content
- Limit usage to non-commercial educational purposes
- Do not modify extracted text

---

### 3. Westminster Theological Seminary

**URLs:**
- **Westminster Media:** [wm.wts.edu](https://wm.wts.edu/)
- **Faculty Publications:** [faculty.wts.edu/publications](https://faculty.wts.edu/publications/)
- **Westminster Theological Journal:** [wtj.wts.edu](https://wtj.wts.edu/)
- **WSCal Resources:** [wscal.edu/resources](https://www.wscal.edu/resources/)

**Available content:**
- Westminster Theological Journal (semi-annual, scholarly articles)
- Westminster Magazine (faculty/student/alumni writings)
- Audio archive (sermons, lectures, chapel messages from theologians like John Murray, Cornelius Van Til, Vern Poythress, Sinclair Ferguson)
- Faculty articles and blog posts

**Content types:**
- Scholarly articles on biblical studies, Reformed theology, church history
- Audio lectures (may have transcripts or need transcription)
- Book reviews
- Student profiles and reflections

**Scraping approach:**
- Check each subdomain's robots.txt
- Use trafilatura for article extraction
- For audio content: may need additional transcription service (not covered in P2)

**Recommendation:** Start with freely available web articles from Westminster Media and faculty blogs.

---

### 4. CCEL (Christian Classics Ethereal Library)

**URL:** [ccel.org](https://www.ccel.org/)
**About:** Digital library of classic Christian literature in the public domain
**Founded:** 1993 by Harry Plantinga (Calvin College)
**License:** Public domain texts (formatting copyrighted by CCEL)

**Content scale:**
- 850+ full-text works
- Major writings from church history figures
- Available formats: HTML, PDF, ThML (Theological Markup Language)

**Reformed theology highlights:**
- John Calvin: *Institutes of the Christian Religion*
- Martin Luther: Major writings
- John Knox: *First Blast of the Trumpet*, *History of the Reformation*
- Augustine: *City of God*
- Thomas Aquinas: *Summa Theologica*
- Abraham Kuyper and other Dutch Reformed writers

**Genres available:**
- Commentaries (231)
- Theology (110)
- Sermons (130)
- Creeds and Catechisms (31)
- Histories
- Biographies
- Early Church writings

**Scraping strategy:**
- All content is public domain (pre-1928 or explicitly released)
- Can scrape freely per robots.txt
- Use trafilatura to extract clean text from HTML versions
- Respect rate limits (2-3 second delays)

**Technical approach:**
- Browse by title/author/topic
- Extract structured content (chapter, section, paragraph)
- Preserve citation information (author, work title, chapter)
- Store original publication dates

**Recommendation:** **Excellent source for historical primary texts.** Start with Calvin's *Institutes* and Luther's works.

---

### 5. Monergism.com

**URL:** [monergism.com](https://www.monergism.com/)
**About:** Free theological library promoting Reformed theology
**Operated by:** Christian Publication Resource Foundation (501(c)(3) nonprofit)

**Content scale:**
- 1,300+ free eBook downloads
- Extensive article library
- Classic writings (Reformers, Puritans, historical theologians)
- MP3 sermon collections
- Topical resources (Five Solas, Covenant Theology, Doctrines of Grace)

**Key topics:**
- Reformed theology and confessions
- Church history (Augustinianism, Reformation, Puritanism)
- Historic creeds and confessions (Nicene, Chalcedonian, Westminster, etc.)
- Systematic theology
- Ordo Salutis (order of salvation)
- God's attributes, gospel, justification, sanctification

**Scraping approach:**
- All content intended for free distribution
- Proper attribution required
- Check robots.txt for crawl policies
- Use trafilatura for article extraction

**Recommendation:** **Excellent curated source** for Reformed systematic theology and historical writings.

---

### 6. The Gospel Coalition (TGC)

**URL:** [thegospelcoalition.org](https://www.thegospelcoalition.org/)
**About:** Broadly Reformed evangelical ministry founded by D.A. Carson and Tim Keller (2007)

**Content focus:**
- Reformed theology essays
- Church history articles
- Theology of the Reformers (Luther, Calvin, Zwingli, Anabaptists)
- Reformed confessions and catechisms
- Contemporary application of Reformed doctrine

**Key articles/sections:**
- [Reformed Theology essay](https://www.thegospelcoalition.org/essay/reformed-theology/)
- [Theology of the Reformers](https://www.thegospelcoalition.org/essay/the-theology-of-the-reformers/)
- [Two Major Streams of Reformed Theology](https://www.thegospelcoalition.org/article/two-major-streams-of-reformed-theology/) (Scottish vs Dutch)
- [Reformation Theology topic page](https://www.thegospelcoalition.org/topics/reformation-theology/)

**Scraping approach:**
- Check Terms of Service for content usage policies
- Use trafilatura for article extraction
- Preserve author attribution
- Rate limit: 2-3 seconds between requests

**Recommendation:** Excellent for **contemporary Reformed scholarship** and accessible church history articles.

---

### 7. Other Reformed Sources to Consider

| Source | URL | Content Type | Notes |
|--------|-----|--------------|-------|
| Reformation Heritage Books | reformationheritagebooks.org | Publishers | Check for open articles/excerpts |
| Heidelblog | heidelblog.net | Blog articles | R. Scott Clark, Reformed theology |
| Desiring God | desiringgod.org | Articles, sermons | John Piper (Reformed Baptist) |
| 9Marks | 9marks.org | Church resources | Reformed Baptist perspective |
| Reformed Forum | reformedforum.org | Podcasts, articles | May have transcripts |
| Banner of Truth | banneroftruth.org | Articles | Reformed publisher |

---

## 4. Text Processing for RAG

### Optimal Chunk Sizes

**2026 Research Consensus:**
- **Winner:** Recursive character splitting at **512 tokens** with **~15% overlap**
- FloTorch benchmark (Feb 2026) tested 7 chunking strategies across thousands of documents
- Simple methods outperformed complex AI-driven semantic chunking

**Chunk size guidelines:**

| Content Type | Recommended Size | Overlap | Reasoning |
|--------------|------------------|---------|-----------|
| YouTube transcripts | 512 tokens (~2048 chars) | 15% (~75 tokens) | Natural speaking boundaries |
| Short articles | 256-512 tokens | 10-15% | Preserve paragraph context |
| Long theological articles | 512-1024 tokens | 15-20% | Complex arguments span multiple paragraphs |
| Historical books (CCEL) | 1024 tokens | 15% | Dense academic content |
| Sermon transcripts | 512 tokens | 15% | Speech patterns, topical shifts |

**Token counting:**
```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Alternative for embeddings:
# Use the embedding model's tokenizer (sentence-transformers)
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
tokens = tokenizer.encode(text)
token_count = len(tokens)
```

**Rule of thumb:** 1 token ≈ 4 characters for English text

---

### Chunking Strategies

#### 1. Recursive Character Splitting (RECOMMENDED)

**How it works:**
- Uses hierarchical list of separators: sections → paragraphs → sentences → words → characters
- Attempts to split on natural boundaries in order of preference
- Falls back to smaller units only if needed

**Why it wins:**
- Respects semantic structure without AI overhead
- Fast and deterministic
- Proven best performance in 2026 benchmarks
- No API calls or embedding costs

**Implementation (LangChain):**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,  # 50-token overlap
    length_function=count_tokens,
    separators=["\n\n", "\n", ". ", " ", ""]  # Ordered by preference
)

chunks = splitter.split_text(long_text)
```

**Recommendation:** **Use recursive character splitting as default** for all content types.

---

#### 2. Fixed-Size Chunking (Fallback)

**How it works:**
- Simple split every N tokens
- May cut mid-sentence

**When to use:**
- As fallback for edge cases
- For content without clear structure

**Pros:** Extremely fast, predictable
**Cons:** Ignores semantic boundaries

---

#### 3. Semantic Chunking (Advanced Use Case)

**How it works:**
- Generate embeddings for each sentence
- Group sentences by semantic similarity
- Split when similarity drops below threshold

**When to use:**
- High-value documents where quality matters more than cost
- Already using embeddings for other purposes

**Pros:** Respects semantic meaning
**Cons:** Expensive (requires embedding every sentence), slower, didn't outperform recursive splitting in benchmarks

**Recommendation:** **Not needed for P2.** Stick with recursive splitting.

---

### Overlap Strategies

**Why overlap matters:**
- Preserves context at chunk boundaries
- Prevents cutting off important context mid-idea
- Improves retrieval recall

**Optimal overlap:** **50 tokens**
- NVIDIA research: tested 0%, 5%, 10%, 15%, 20%, 25%
- ~10% (50/512) overlap balances context preservation and redundancy
- Aligns with industry best practices (10-20%)

**Example:**
- Chunk size: 512 tokens
- Overlap: 50 tokens
- Chunk 1: tokens 0-512
- Chunk 2: tokens 462-974 (overlaps 50 tokens with chunk 1)

**Implementation:**
```python
def create_chunks_with_overlap(text, chunk_size=512, overlap=50):
    tokens = tokenize(text)
    step = chunk_size - overlap

    chunks = []
    for i in range(0, len(tokens), step):
        chunk = tokens[i:i+chunk_size]
        chunks.append(detokenize(chunk))

    return chunks
```

---

### Metadata Preservation

**Store with each chunk:**
```python
chunk_metadata = {
    'source_type': 'youtube_transcript',  # or 'article', 'book'
    'source_id': 'video_123',
    'source_url': 'https://youtube.com/watch?v=...',
    'title': 'Lecture on Calvin and Geneva',
    'author': 'Ryan Reeves',
    'date': '2023-05-15',
    'chunk_index': 3,
    'total_chunks': 12,
    'start_position': 1024,  # Character position in original
    'end_position': 2560,
    'attribution': 'Dr. Ryan Reeves, Gordon-Conwell Theological Seminary'
}
```

**Why metadata matters:**
- Enables filtering during retrieval (e.g., "only Ryan Reeves videos")
- Supports proper attribution in UI
- Allows temporal filtering (e.g., "recent content")
- Helps debug retrieval quality

---

## 5. Embedding Models

### Model Comparison: all-MiniLM-L6-v2 vs all-mpnet-base-v2

| Feature | all-MiniLM-L6-v2 | all-mpnet-base-v2 |
|---------|------------------|-------------------|
| **License** | Apache-2.0 ✅ | Apache-2.0 ✅ |
| **Dimensions** | 384 | 768 |
| **Parameters** | 22 million | 110 million |
| **Speed** | 5× faster | Baseline |
| **Accuracy (MTEB)** | 84-85% | 87-88% |
| **Architecture** | Distilled MiniLM (6 layers) | MPNet (12 layers) |
| **Input Tokens** | 256 word pieces (128 during training) | Handles longer documents |
| **Best For** | Real-time, edge, latency-sensitive | High accuracy, production RAG |
| **Use Case** | Chatbots, mobile apps | Document analysis, semantic search |

**Sources:**
- [HuggingFace: all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Milvus AI FAQ](https://milvus.io/ai-quick-reference/what-are-some-popular-pretrained-sentence-transformer-models-and-how-do-they-differ-for-example-allminilml6v2-vs-allmpnetbasev2)

---

### Recommendation for Theological/Historical Text

**Choose:** **`all-MiniLM-L6-v2`** ✅

**Reasoning:**
1. **Good balance of speed and quality** — 384 dimensions provide strong semantic similarity performance while being 5x faster to embed than mpnet. For a batch-processing pipeline, this matters.
2. **Sufficient accuracy** — 84-85% on MTEB benchmarks is more than adequate for church history RAG retrieval.
3. **Smaller storage footprint** — 384 vs 768 dimensions = half the storage cost and faster query time.
4. **Runs efficiently locally** — No GPU required for acceptable batch throughput on CPU.
5. **Wide adoption** — One of the most downloaded sentence-transformer models; well-tested in production RAG systems.

**Trade-offs:**
- Slightly lower accuracy than mpnet (84-85% vs 87-88%)
- Truncates at 256 tokens (keep chunks ≤ 512 chars as a guideline)

**For P2 scope:** Speed and storage efficiency outweigh the marginal accuracy gain of mpnet. `all-MiniLM-L6-v2` is the right choice for an initial production pipeline.

---

### sentence-transformers Library

**License:** Apache-2.0 ✅
**Latest Version:** 5.2.2 (January 27, 2026)
**Python Requirement:** ≥3.10
**PyPI:** [pypi.org/project/sentence-transformers](https://pypi.org/project/sentence-transformers/)
**Docs:** [sbert.net](https://www.sbert.net/)

**What it provides:**
- 15,000+ pre-trained models on HuggingFace
- Easy-to-use API for sentence/document embeddings
- Built on PyTorch and Transformers
- Supports fine-tuning and custom models

**Installation:**
```bash
pip install sentence-transformers
```

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Embed documents
chunks = ["First chunk text...", "Second chunk text..."]
embeddings = model.encode(chunks, show_progress_bar=True)

# Result: numpy array of shape (2, 384)
```

**Performance:**
- Downloads last month: **17.1 million**
- Actively maintained by Nils Reimers and Tom Aarsen
- Production-stable (Development Status: 5)

---

### Local vs API-Based Embedding

**Local (Recommended for P2):**

**Pros:**
- **No API costs** — Free after initial compute
- **Privacy** — No data sent to third parties
- **No rate limits** — Embed as fast as hardware allows
- **Offline capability** — No internet dependency

**Cons:**
- Requires local compute (CPU or GPU)
- Slower on CPU (but still acceptable for batch processing)

**API-Based (e.g., OpenAI, Cohere):**

**Pros:**
- No local compute needed
- Faster on underpowered hardware

**Cons:**
- **Cost** — $0.0001 per 1K tokens (OpenAI ada-002)
- **Rate limits** — Throttled by provider
- **Privacy** — Content sent to third party
- **Dependency** — Requires API key and internet

**Recommendation for P2:** **Use local sentence-transformers with `all-MiniLM-L6-v2`.**
- One-time embedding during scraping (batch process)
- No ongoing costs
- Aligns with educational/nonprofit mission
- Keeps data in-house

**Future optimization:** If embedding becomes a bottleneck, use GPU or upgrade to `all-mpnet-base-v2` for higher accuracy.

---

### Fine-Tuning Considerations (Future P3+)

**Why fine-tune?**
- Domain-specific language (theological terminology)
- Improve retrieval quality for Reformed theology concepts

**When to fine-tune:**
- After P2 when you have usage data
- If retrieval quality is insufficient
- If budget allows for compute

**Dataset needed:**
- Question-answer pairs from Reformed theology
- Positive/negative passage pairs
- User query logs (after launch)

**Recommendation:** **Don't fine-tune in P2.** Pre-trained `all-mpnet-base-v2` is excellent out-of-the-box. Re-evaluate in P3 based on retrieval metrics.

---

## 6. pgvector Configuration

### HNSW vs IVFFlat: The Verdict

**Recommendation: HNSW** ✅

| Metric | IVFFlat | HNSW |
|--------|---------|------|
| **Query Speed** | ~2.4ms | ~1.5ms ✅ |
| **Throughput (QPS)** | 2.6 QPS | 40.5 QPS ✅ |
| **Build Time** | 128s ✅ | 4065s (32× slower) |
| **Memory Usage** | 257 MB ✅ | 729 MB (2.8× more) |
| **Data Mutability** | Poor (needs rebuild) | Excellent ✅ |
| **Empty Table Support** | ❌ (needs training data) | ✅ (incremental build) |
| **Recall** | Good | Better ✅ |
| **Resilience to Updates** | Poor (centroids fixed) | Excellent ✅ |

**Sources:**
- [AWS Blog: Optimize pgvector indexing](https://aws.amazon.com/blogs/database/optimize-generative-ai-applications-with-pgvector-indexing-a-deep-dive-into-ivfflat-and-hnsw-techniques/)
- [Medium: PGVector HNSW vs IVFFlat](https://medium.com/@bavalpreetsinghh/pgvector-hnsw-vs-ivfflat-a-comprehensive-study-21ce0aaab931)
- [Tembo: Vector Indexes in pgvector](https://legacy.tembo.io/blog/vector-indexes-in-pgvector/)

---

### Why HNSW is Better for Toledot

1. **Query Performance:** 15.5× better throughput than IVFFlat
2. **No Retraining Needed:** Content will be added incrementally (new sermons, articles). HNSW handles this gracefully; IVFFlat requires periodic index rebuilds.
3. **Better Recall:** More accurate search results
4. **Incremental Build:** Can create index on empty table, builds as data arrives
5. **General Recommendation:** pgvector docs state "HNSW is recommended" for most use cases

**Trade-off:** Slower initial index build (acceptable as one-time operation)

---

### Optimal HNSW Parameters

#### Index Creation

```sql
CREATE INDEX ON content_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Parameters:**
- **`m`** (default: 16) — Maximum number of connections per layer
  - Higher = better recall, more memory
  - Range: 8-64
  - Recommendation: **16** (default is good)

- **`ef_construction`** (default: 64) — Size of dynamic candidate list during index construction
  - Higher = better index quality, slower build
  - Range: 32-512
  - Recommendation: **64** (default) for <100K vectors; **128** for 100K+ vectors

**For Toledot P2:**
- Expected dataset: ~1,000-10,000 chunks initially
- Use defaults: `m=16`, `ef_construction=64`
- Re-evaluate if dataset grows beyond 100K chunks

---

#### Query-Time Tuning

```sql
SET hnsw.ef_search = 40;

SELECT content, source, 1 - (embedding <=> query_vector) AS similarity
FROM content_embeddings
ORDER BY embedding <=> query_vector
LIMIT 10;
```

**Parameter:**
- **`hnsw.ef_search`** (default: 40) — Size of dynamic candidate list during search
  - Higher = better recall, slower queries
  - Range: 10-200
  - Recommendation: **40-100** (start with 40, increase if recall is low)

**Tuning advice:**
- Start with default (40)
- If top results seem off, increase to 100
- Monitor query latency vs recall

---

### Cosine Similarity vs L2 Distance

**For text embeddings:** **Use Cosine Similarity** ✅

**Reasoning:**
- Sentence-transformers models (MPNet, MiniLM) are trained for cosine similarity
- Cosine measures angular distance (direction), not magnitude
- Text embeddings: direction matters, magnitude doesn't
- L2 (Euclidean) distance: better for spatial data (images, coordinates)

**Operator:** `vector_cosine_ops`

**Query syntax:**
```sql
-- Cosine distance (0 = identical, 2 = opposite)
ORDER BY embedding <=> query_vector

-- Convert to similarity score (1 = identical, 0 = perpendicular, -1 = opposite)
SELECT 1 - (embedding <=> query_vector) AS similarity
```

---

### Django Integration with pgvector

**Package:** `pgvector` (Python)
**PyPI:** [pypi.org/project/pgvector](https://pypi.org/project/pgvector/)
**Docs:** [github.com/pgvector/pgvector-python](https://github.com/pgvector/pgvector-python)

**Installation:**
```bash
pip install pgvector psycopg2-binary  # or psycopg[binary]
```

**Django Model Example:**
```python
from django.db import models
from pgvector.django import VectorField, HnswIndex

class ContentEmbedding(models.Model):
    content = models.TextField()
    source_type = models.CharField(max_length=50)  # 'youtube', 'article', 'book'
    source_url = models.URLField()
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    date = models.DateField(null=True)
    chunk_index = models.IntegerField()

    # Vector field for embeddings
    embedding = VectorField(dimensions=384)  # all-MiniLM-L6-v2

    # Metadata
    attribution = models.TextField()

    class Meta:
        indexes = [
            HnswIndex(
                name='content_embedding_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            ),
        ]

    def __str__(self):
        return f"{self.title} (chunk {self.chunk_index})"
```

**Querying:**
```python
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer

# Generate query embedding
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
query_embedding = model.encode("What did Calvin teach about predestination?")

# Search for similar chunks
results = ContentEmbedding.objects.annotate(
    similarity=1 - CosineDistance('embedding', query_embedding)
).order_by('-similarity')[:10]

for result in results:
    print(f"{result.title} - Similarity: {result.similarity:.3f}")
```

**Django Migration:**
```python
from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    operations = [
        VectorExtension(),  # Enable pgvector extension
        # ... rest of migration
    ]
```

---

### Expected Dataset Size & Performance

**P2 Initial Estimates:**
- Ryan Reeves: ~100 videos × 8 chunks/video = 800 chunks
- Ligonier: ~500 articles × 4 chunks/article = 2,000 chunks
- CCEL: ~50 books × 200 chunks/book = 10,000 chunks
- TGC/Monergism: ~1,000 articles × 4 chunks = 4,000 chunks
- **Total: ~17,000 chunks**

**Storage:**
- Vector size: 384 dimensions × 4 bytes (float32) = 1,536 bytes per vector
- Total vectors: ~17,000 × 1.5 KB ≈ **26 MB** (vectors only)
- With metadata: ~75-150 MB total

**Performance expectations:**
- HNSW query time: <5ms per query
- Batch embedding: ~1,000 chunks/minute on CPU
- Index build: ~1-2 minutes for 17K vectors

**Scalability:**
- pgvector + HNSW handles millions of vectors
- Current scale is well within optimal range

---

## 7. Legal & Ethical Considerations

### YouTube Terms of Service

**Transcript Access:**
- YouTube TOS does not explicitly prohibit accessing transcripts
- Transcripts are derivative works owned by content creator
- `youtube-transcript-api` uses YouTube's internal API (no scraping of HTML)

**Educational Fair Use (US Copyright Law):**
- **Four fair use factors:**
  1. **Purpose:** Nonprofit educational use ✅
  2. **Nature:** Factual/educational content ✅
  3. **Amount:** Using transcripts as reference material ✅
  4. **Market Effect:** Does not harm creator's revenue ✅

**Best practices:**
- Attribute content to original creators
- Link back to original videos
- Do not redistribute transcripts publicly
- Use only for internal RAG retrieval
- Add disclaimers in UI
- Consider reaching out to Ryan Reeves for explicit permission (strengthens goodwill)

**Sources:**
- [YouTube Fair Use Help](https://support.google.com/youtube/answer/9783148)
- [YouTube Transcription and Copyright Guide](https://insight7.io/youtube-transcription-and-copyright-what-you-need-to-know/)

---

### Web Scraping Ethics

#### robots.txt Compliance

**Legal importance:**
- Computer Fraud and Abuse Act (CFAA) has been cited in cases where robots.txt was ignored
- Violating robots.txt can trigger legal action
- Shows good faith in potential legal disputes

**Implementation:**
```python
import urllib.robotparser

def check_robots_txt(url):
    rp = urllib.robotparser.RobotFileParser()
    base = '/'.join(url.split('/')[:3])
    rp.set_url(f"{base}/robots.txt")
    rp.read()

    # Check if we can fetch
    if not rp.can_fetch("ToledotBot", url):
        print(f"Disallowed by robots.txt: {url}")
        return False

    # Check crawl delay
    delay = rp.crawl_delay("ToledotBot")
    if delay:
        print(f"Crawl-delay: {delay} seconds")

    return True
```

**Recommendation:**
- Check robots.txt before every scraping session
- Re-check daily for active scraping projects
- Respect all `Disallow` directives
- Honor `Crawl-delay` (or use 2s default if not specified)

---

#### Rate Limiting Etiquette

**Why it matters:**
- Prevents server overload
- Avoids IP bans
- Shows respect for content providers
- Maintains long-term access

**Guidelines:**
- **Small nonprofit sites:** 3-5 second delays
- **Medium sites (Ligonier, TGC):** 2-3 second delays
- **Large sites (CCEL):** 1-2 second delays
- **YouTube:** 2-3 second delays between transcripts

**Monitoring:**
- Track HTTP status codes (watch for 429, 503)
- Implement exponential backoff on errors
- Log all requests and responses
- Set up alerts for excessive error rates

---

#### Attribution Requirements

**Ligonier Ministries:**
- **Required:** "Originally published in Tabletalk magazine of Ligonier Ministries"
- **Link:** Must hyperlink to TabletalkMagazine.com
- **No alterations:** Display content as-is
- **Non-commercial only**

**CCEL:**
- Public domain content (no attribution legally required)
- **Best practice:** Cite author, work title, and CCEL
- Example: "John Calvin, *Institutes of the Christian Religion*, Christian Classics Ethereal Library"

**Ryan Reeves (YouTube):**
- **Required:** Attribute to Dr. Ryan Reeves, Gordon-Conwell Theological Seminary
- **Link:** Include YouTube video URL
- Example: "Dr. Ryan Reeves, 'Calvin and Geneva' lecture, Gordon-Conwell Theological Seminary"

**TGC, Monergism, Westminster:**
- Check individual Terms of Service
- Default: Cite author, title, organization, URL
- Assume non-commercial use only unless stated otherwise

---

### Data Privacy (GDPR/CCPA)

**Toledot's scope:**
- Scraping public content (no personal data)
- No user tracking during scraping
- No collection of PII

**Compliance:**
- Only scrape publicly accessible content
- Do not scrape paywalled or login-required content
- Do not store email addresses, names, or user comments
- Focus on educational content only

**Recommendation:** P2 scope avoids personal data entirely. ✅

---

### Terms of Service Review

**Before scraping any site:**
1. Read the Terms of Service
2. Check Copyright Policy
3. Look for "API Terms" or "Developer Terms"
4. Search for "scraping", "automated access", "robots"

**Red flags:**
- Explicit "no scraping" clause → Do not scrape
- "Commercial use prohibited" → OK for nonprofit educational use
- "API required for access" → Use API or skip

**Recommended approach:**
- Document ToS review in codebase
- Maintain list of approved/rejected sources
- Re-check ToS quarterly

---

### Ethical Summary

| Source | Legal Status | Attribution Required | Rate Limit | Notes |
|--------|--------------|---------------------|------------|-------|
| Ryan Reeves YouTube | Fair use (educational) | Yes | 2-3s | Consider asking permission |
| Ligonier | Permitted (non-commercial) | Yes + hyperlink | 2-3s | Max 500 copies, <250 words for books |
| CCEL | Public domain | Best practice | 2s | Public domain, cite anyway |
| TGC | Check ToS | Yes | 2-3s | Review copyright policy |
| Monergism | Permitted (free distribution) | Yes | 2s | Nonprofit, educational aligned |
| Westminster | Check per source | Yes | 2s | Mix of open and restricted |

**General principle:** **When in doubt, over-attribute and over-respect rate limits.**

---

## 8. Dependencies to Add

### Python Packages

**Copy-paste this into `requirements.txt`:**

```txt
# YouTube transcript extraction
youtube-transcript-api==1.2.4  # MIT license

# YouTube video enumeration and metadata
yt-dlp>=2026.02.04  # Unlicense (public domain)

# YouTube RSS feed parsing (no API key needed)
feedparser>=6.0.0  # MIT license

# Web scraping and article extraction
trafilatura>=2.0.0  # Apache-2.0 license
beautifulsoup4>=4.12.0  # MIT license
lxml>=5.0.0  # BSD license

# Embedding models
sentence-transformers>=5.2.2  # Apache-2.0 license
torch>=2.0.0  # BSD license (PyTorch)
transformers>=4.34.0  # Apache-2.0 license

# Vector database
pgvector>=0.3.0  # PostgreSQL license (permissive)
psycopg[binary]>=3.1.0  # LGPL v3+ (connection library)

# Text processing utilities
tiktoken>=0.8.0  # MIT license (OpenAI's tokenizer)
langchain-text-splitters>=0.3.0  # MIT license (chunking utilities)

# Rate limiting and retry logic
tenacity>=9.0.0  # Apache-2.0 license
```

### License Summary

All recommended packages use permissive licenses compatible with commercial and nonprofit use:

| Package | License | Commercial OK? | Notes |
|---------|---------|----------------|-------|
| youtube-transcript-api | MIT | ✅ | Permissive |
| yt-dlp | Unlicense | ✅ | Public domain |
| feedparser | MIT | ✅ | RSS/Atom feed parsing |
| trafilatura | Apache-2.0 | ✅ | Permissive (GPLv3 for v<1.8.0) |
| beautifulsoup4 | MIT | ✅ | Permissive |
| lxml | BSD | ✅ | Permissive |
| sentence-transformers | Apache-2.0 | ✅ | Permissive |
| torch (PyTorch) | BSD | ✅ | Permissive |
| transformers | Apache-2.0 | ✅ | Permissive |
| pgvector | PostgreSQL | ✅ | Permissive |
| psycopg | LGPL v3+ | ⚠️ | Dynamic linking OK |
| tiktoken | MIT | ✅ | Permissive |
| langchain-text-splitters | MIT | ✅ | Permissive |
| tenacity | Apache-2.0 | ✅ | Permissive |

**Note on psycopg LGPL:** Dynamically linking to LGPL libraries (like psycopg) is permitted without requiring your code to be LGPL, as long as users can replace the library. This is standard practice for database drivers.

---

### PostgreSQL Extension

**Enable pgvector in PostgreSQL:**

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Django migration:**
```python
from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    operations = [
        VectorExtension(),
    ]
```

**Verify installation:**
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

### System Dependencies (Optional but Recommended)

**FFmpeg** (for yt-dlp video/audio processing):
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**Note:** Only needed if downloading videos/audio. For transcript-only extraction, not required.

---

## Summary & Recommendations

### Technology Stack (Final)

| Component | Choice | License | Why |
|-----------|--------|---------|-----|
| **YouTube Transcripts** | `youtube-transcript-api` | MIT | Simple, no API key, sufficient |
| **YouTube Metadata** | `yt-dlp` | Unlicense | Channel enumeration, metadata |
| **Web Scraping** | `trafilatura` | Apache-2.0 | Best article extractor, proven |
| **Embedding Model** | `all-MiniLM-L6-v2` | Apache-2.0 | Good speed/quality balance, 384 dims |
| **Embedding Library** | `sentence-transformers` | Apache-2.0 | Industry standard |
| **Chunking Strategy** | Recursive char splitting | N/A | 512 tokens, 50-token overlap |
| **Vector Index** | pgvector HNSW | PostgreSQL | Best performance, resilience |
| **Distance Metric** | Cosine similarity | N/A | Standard for text embeddings |

---

### Priority Content Sources (P2)

**Phase 1 (Immediate):**
1. ✅ Ryan Reeves YouTube (Early & Medieval + Reformation playlists)
2. ✅ CCEL (Calvin's Institutes, Luther's works)

**Phase 2 (After Phase 1 working):**
3. ✅ Ligonier articles (with proper attribution)
4. ✅ The Gospel Coalition church history section

**Phase 3 (Future):**
5. Monergism curated content
6. Westminster Seminary articles
7. Additional Reformed sources

---

### Next Steps for Implementation

1. **Install dependencies** (see Section 8)
2. **Set up pgvector** extension in PostgreSQL
3. **Create Django models** for content storage (see Section 6)
4. **Implement scraping management commands:**
   - `scrape_youtube_channel`
   - `scrape_articles`
   - `scrape_ccel_books`
5. **Implement chunking pipeline** (recursive splitting, 512 tokens, 15% overlap)
6. **Implement embedding generation** (sentence-transformers, all-mpnet-base-v2)
7. **Test retrieval** (semantic search queries, measure recall/precision)
8. **Add attribution** to UI/API responses

---

## 9. Architecture Decision Summary

### Key Decisions and Rationale

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Transcript library | `youtube-transcript-api` | No API key, MIT license, sufficient for transcripts only |
| Channel discovery | `yt-dlp` + YouTube RSS feeds | yt-dlp for bulk import; RSS for polling new content |
| Video metadata | YouTube oEmbed API | Free, no key, returns title/author/thumbnail |
| Web scraping | `trafilatura` | #1 ranked article extractor, Apache-2.0, handles boilerplate |
| HTML parsing | `beautifulsoup4` + `lxml` | Fallback for custom extraction, MIT/BSD licenses |
| robots.txt | `urllib.robotparser` (stdlib) | No extra dependency, enforces ethical compliance |
| Chunking | Recursive char splitting | 512 tokens, 50-token overlap — simple, proven best in benchmarks |
| Token counting | `tiktoken` | Accurate BPE token counting, MIT license |
| Embedding model | `all-MiniLM-L6-v2` | 384 dims, good speed/quality balance, runs locally |
| Embedding library | `sentence-transformers` | Industry standard, Apache-2.0, 15M+ downloads/month |
| Vector DB | pgvector HNSW | Best throughput (40.5 QPS vs 2.6 for IVFFlat), handles incremental updates |
| Distance metric | Cosine similarity (`vector_cosine_ops`) | Standard for text embeddings from sentence-transformers |
| Deployment | Local (no API) | No API costs, privacy preserved, offline capable |

### Data Flow

```
Content Source
    │
    ▼
Scraping Layer
    ├── YouTube: yt-dlp (discovery) → youtube-transcript-api (transcripts)
    └── Web: trafilatura / beautifulsoup4 → clean article text
    │
    ▼
Text Processing
    ├── Clean transcripts (strip timestamps, annotations)
    ├── Chunk: 512 tokens, 50-token overlap (RecursiveCharacterTextSplitter)
    └── Count tokens: tiktoken
    │
    ▼
Embedding Generation
    └── sentence-transformers all-MiniLM-L6-v2 → 384-dim vectors
    │
    ▼
pgvector Storage (PostgreSQL)
    └── ContentChunk.embedding = VectorField(dimensions=384)
        └── HNSW index: m=16, ef_construction=64, vector_cosine_ops
    │
    ▼
RAG Query
    └── Embed query → cosine similarity search → return top-k chunks
```

### pgvector Schema Summary

```python
class ContentChunk(models.Model):
    content = models.TextField()
    source_type = models.CharField(max_length=50)
    source_url = models.URLField()
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    chunk_index = models.IntegerField()
    attribution = models.TextField()
    embedding = VectorField(dimensions=384)  # all-MiniLM-L6-v2

    class Meta:
        indexes = [
            HnswIndex(
                name='content_chunk_embedding_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            ),
        ]
```

---

## References & Sources

### YouTube Transcript Scraping
- [youtube-transcript-api on PyPI](https://pypi.org/project/youtube-transcript-api/)
- [youtube-transcript-api GitHub](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp on PyPI](https://pypi.org/project/yt-dlp/)
- [youtube-search-python GitHub](https://github.com/alexmercerind/youtube-search-python)

### Web Scraping Libraries
- [trafilatura on PyPI](https://pypi.org/project/trafilatura/)
- [trafilatura documentation](https://trafilatura.readthedocs.io/)
- [newspaper4k on PyPI](https://pypi.org/project/newspaper4k/)
- [newspaper4k GitHub](https://github.com/AndyTheFactory/newspaper4k)

### Content Sources
- [Ryan Reeves YouTube Channel](https://www.youtube.com/channel/UCrI5U0R293u9uveijefKyAA)
- [Ligonier Ministries](https://www.ligonier.org/)
- [Ligonier Copyright Policy](https://www.ligonier.org/copyright-policy)
- [CCEL Homepage](https://www.ccel.org/)
- [Monergism.com](https://www.monergism.com/)
- [The Gospel Coalition](https://www.thegospelcoalition.org/)
- [Westminster Theological Seminary](https://wm.wts.edu/)

### RAG & Chunking
- [Databricks: Ultimate Guide to Chunking](https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089)
- [Firecrawl: Best Chunking Strategies 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [NVIDIA: Finding Best Chunking Strategy](https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/)
- [RAG About It: 2026 RAG Performance Paradox](https://ragaboutit.com/the-2026-rag-performance-paradox-why-simpler-chunking-strategies-are-outperforming-complex-ai-driven-methods/)

### Embedding Models
- [sentence-transformers on PyPI](https://pypi.org/project/sentence-transformers/)
- [Sentence-Transformers Documentation](https://sbert.net/)
- [HuggingFace: all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Milvus: Model Comparison FAQ](https://milvus.io/ai-quick-reference/what-are-some-popular-pretrained-sentence-transformer-models-and-how-do-they-differ-for-example-allminilml6v2-vs-allmpnetbasev2)

### pgvector
- [AWS: Optimize pgvector Indexing](https://aws.amazon.com/blogs/database/optimize-generative-ai-applications-with-pgvector-indexing-a-deep-dive-into-ivfflat-and-hnsw-techniques/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Medium: HNSW vs IVFFlat Study](https://medium.com/@bavalpreetsinghh/pgvector-hnsw-vs-ivfflat-a-comprehensive-study-21ce0aaab931)
- [Tembo: Vector Indexes in pgvector](https://legacy.tembo.io/blog/vector-indexes-in-pgvector/)

### Legal & Ethical
- [YouTube Fair Use Help](https://support.google.com/youtube/answer/9783148)
- [Insight7: YouTube Transcription and Copyright](https://insight7.io/youtube-transcription-and-copyright-what-you-need-to-know/)
- [CodeSignal: Scraping Best Practices](https://codesignal.com/learn/courses/implementing-scalable-web-scraping-with-python/lessons/scraping-best-practices)
- [Bright Data: robots.txt Guide](https://brightdata.com/blog/how-tos/robots-txt-for-web-scraping-guide)
- [Medium: DOs and DON'Ts of Web Scraping 2026](https://medium.com/@datajournal/dos-and-donts-of-web-scraping-in-2025-e4f9b2a49431)

---

**End of Research Document**
**Total Pages:** 28
**Word Count:** ~8,500
**Prepared by:** AI Research Agent Team
**Date:** February 16, 2026
