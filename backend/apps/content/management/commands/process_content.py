"""
Django management command to process raw content into chunks with embeddings.

Usage examples:
    python manage.py process_content  # Process all unprocessed items
    python manage.py process_content --source-id 1  # Process items from specific source
    python manage.py process_content --batch-size 50
    python manage.py process_content --dry-run
"""

from typing import List

import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import ContentChunk, ContentItem, Source
from apps.content.utils import chunk_text, clean_transcript, count_tokens


class Command(BaseCommand):
    """Process raw content into chunks with embeddings."""

    help = "Process unprocessed content items into chunks with embeddings for RAG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embedding_model = None

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--source-id",
            type=int,
            help="Process only items from this source ID",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,
            help="Number of items to process per run (default: 10)",
        )
        parser.add_argument(
            "--model-name",
            type=str,
            default="all-MiniLM-L6-v2",
            help="Embedding model to use (default: all-MiniLM-L6-v2)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be processed without making changes",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        source_id = options["source_id"]
        batch_size = options["batch_size"]
        model_name = options["model_name"]
        dry_run = options["dry_run"]

        try:
            # Get unprocessed items
            queryset = ContentItem.objects.filter(is_processed=False)

            if source_id:
                try:
                    source = Source.objects.get(id=source_id)
                    queryset = queryset.filter(source=source)
                    self.stdout.write(f"Processing items from source: {source.name}")
                except Source.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Source with ID {source_id} not found"))
                    return

            # Apply batch size
            items = queryset.select_related('source')[:batch_size]
            total_count = queryset.count()

            if not items:
                self.stdout.write(self.style.WARNING("No unprocessed items found"))
                return

            self.stdout.write(f"Found {total_count} unprocessed item(s)")
            self.stdout.write(f"Processing batch of {len(items)} item(s)")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
                for item in items:
                    self.stdout.write(f"  - [{item.id}] {item.title} ({len(item.raw_text)} chars)")
                return

            # Load embedding model (lazy load)
            if not dry_run:
                self.stdout.write(f"Loading embedding model: {model_name}")
                self._load_embedding_model(model_name)

            # Process items
            stats = {"processed": 0, "failed": 0, "total_chunks": 0}

            for idx, item in enumerate(items, 1):
                self.stdout.write(f"\n[{idx}/{len(items)}] Processing: {item.title}")

                try:
                    chunks_created = self._process_item(item)
                    self.stdout.write(self.style.SUCCESS(f"  Created {chunks_created} chunk(s)"))
                    stats["processed"] += 1
                    stats["total_chunks"] += chunks_created

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Failed: {str(e)}"))
                    stats["failed"] += 1

            # Print summary
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} item(s)"))
            self.stdout.write(self.style.SUCCESS(f"Total chunks created: {stats['total_chunks']}"))
            if stats["failed"] > 0:
                self.stdout.write(self.style.ERROR(f"Failed: {stats['failed']} item(s)"))
            if total_count > len(items):
                self.stdout.write(self.style.WARNING(f"Remaining: {total_count - len(items)} item(s)"))
            self.stdout.write("=" * 50)

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\n\nInterrupted by user"))

    def _load_embedding_model(self, model_name: str):
        """Load the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise Exception(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )

        self._embedding_model = SentenceTransformer(model_name)
        self.stdout.write(f"Model loaded: {model_name}")

    def _process_item(self, item: ContentItem) -> int:
        """Process a single content item."""
        with transaction.atomic():
            # Clean text based on content type
            if item.content_type == ContentItem.ContentType.TRANSCRIPT:
                processed_text = clean_transcript(item.raw_text)
            else:
                # For articles, just normalize whitespace
                processed_text = self._normalize_text(item.raw_text)

            # Update processed text
            item.processed_text = processed_text
            item.token_count = count_tokens(processed_text)

            # Create chunks
            chunks = chunk_text(processed_text, max_tokens=512, overlap=50)

            if not chunks:
                self.stdout.write(self.style.WARNING("  No chunks generated (empty text)"))
                item.is_processed = True
                item.save()
                return 0

            # Generate embeddings in batches
            chunk_texts = [chunk[0] for chunk in chunks]
            embeddings = self._generate_embeddings_batch(chunk_texts)

            # Create ContentChunk objects
            chunk_objects = []
            for idx, ((chunk_text, token_count), embedding) in enumerate(zip(chunks, embeddings)):
                chunk_obj = ContentChunk(
                    content_item=item,
                    chunk_text=chunk_text,
                    chunk_index=idx,
                    token_count=token_count,
                    embedding=embedding.tolist(),  # Convert numpy array to list
                    metadata={},
                )
                chunk_objects.append(chunk_obj)

            # Bulk create chunks
            ContentChunk.objects.bulk_create(chunk_objects)

            # Mark as processed
            item.is_processed = True
            item.save()

            return len(chunk_objects)

    def _normalize_text(self, text: str) -> str:
        """Normalize text by fixing whitespace and encoding issues."""
        import re

        # Fix encoding issues
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart single quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '--',  # En/em dashes
            '\u2026': '...',  # Ellipsis
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Fix multiple spaces
        text = re.sub(r' +', ' ', text)

        # Fix multiple newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)

        return text.strip()

    def _generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts."""
        if not self._embedding_model:
            raise Exception("Embedding model not loaded")

        all_embeddings = []

        # Process in batches to avoid memory issues
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self._embedding_model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            all_embeddings.extend(embeddings)

        return all_embeddings
