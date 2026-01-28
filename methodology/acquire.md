# Acquisition: Collecting PDF Corpora

## Overview

The acquisition stage collects PDF documents from a research organization's public website. The goal is a local directory of PDFs that represents the organization's published research output.

## Methods

### Web Scraping

Most organizations publish a "publications" or "research" page with links to downloadable PDFs. A scraper walks this page (and any pagination) to collect PDF URLs, then downloads them with polite delays.

Recommended practices:
- Respect `robots.txt`
- Use 0.3-1.0 second delays between requests
- Limit concurrent downloads (3 max)
- Log all downloads with timestamps and HTTP status codes

### Direct Download

Some organizations provide bulk access via institutional repositories, SSRN, or similar platforms. In these cases, PDFs can be downloaded directly with standard HTTP tools.

### Manual Collection

For small corpora (< 50 documents), manual download is viable and avoids scraping complexity.

## Output

The acquisition stage produces:
- A directory of PDF files
- (Optional) A manifest file mapping filenames to source URLs and download timestamps

## What Goes Into the Pipeline

The build script (`scripts/build_index.py`) takes a `--pdf_dir` argument pointing to the acquired PDF directory. It processes every `.pdf` file in that directory. Files that fail text extraction (scanned images without OCR) are logged and skipped.

## Skip Lists

For corpora containing scanned or image-heavy PDFs that `pdftotext` cannot extract, create a skip list (one filename per line) and pass it with `--skip_list`. These files are excluded from processing without failing the build.
