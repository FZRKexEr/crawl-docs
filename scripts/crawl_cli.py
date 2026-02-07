#!/usr/bin/env python3
"""CLI tool for crawling documentation sites and saving as local markdown files."""

import argparse
import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    DefaultMarkdownGenerator,
)
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


def get_markdown(result) -> str:
    """Extract markdown string from a crawl result."""
    md = result.markdown
    if md is None:
        return ""
    if isinstance(md, str):
        return md
    return getattr(md, "raw_markdown", "") or getattr(md, "fit_markdown", "") or ""


def sanitize_filename(url: str) -> str:
    """Convert URL path to a safe filename."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    path = re.sub(r"[^\w\-.]", "_", path)
    return path[:100]


def get_output_dir(url: str, base_dir: str) -> Path:
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_")
    return Path(base_dir) / domain


async def crawl_page(url: str, output_dir: str) -> None:
    out_dir = get_output_dir(url, output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    browser_config = BrowserConfig(headless=True, browser_type="chromium")
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(),
    )

    print(f"Crawling {url} ...")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            print(f"Error: {result.error_message}", file=sys.stderr)
            sys.exit(1)

        content = get_markdown(result)
        filename = sanitize_filename(url) + ".md"
        filepath = out_dir / filename

        title = getattr(result, "title", "") or url
        filepath.write_text(f"# {title}\n\nURL: {url}\n\n{content}")

        print(f"Saved: {filepath}")
        print(f"Size: {len(content):,} chars")


async def crawl_site(url: str, max_depth: int, max_pages: int, output_dir: str) -> None:
    out_dir = get_output_dir(url, output_dir)
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    browser_config = BrowserConfig(headless=True, browser_type="chromium")
    crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=max_depth,
        include_external=False,
        max_pages=max_pages,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(),
        deep_crawl_strategy=crawl_strategy,
    )

    print(f"Deep crawling {url} (depth={max_depth}, max_pages={max_pages}) ...")

    pages = []
    errors = 0

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(url=url, config=run_config)
        if not isinstance(results, list):
            results = [results]

        for i, r in enumerate(results):
            if not r.success:
                errors += 1
                continue
            content = get_markdown(r)
            if not content.strip():
                continue

            title = getattr(r, "title", "") or r.url
            depth = getattr(r, "depth", 0) or 0
            filename = f"{i:03d}_{sanitize_filename(r.url)}.md"
            filepath = pages_dir / filename

            filepath.write_text(f"# {title}\n\nURL: {r.url}\nDepth: {depth}\n\n{content}")

            pages.append({
                "file": str(filepath),
                "url": r.url,
                "title": title,
                "depth": depth,
                "size": len(content),
            })

    pages.sort(key=lambda p: (p["depth"], p["url"]))

    # Write index
    index_path = out_dir / "index.md"
    lines = [
        f"# Crawl Index: {url}\n",
        f"Pages: {len(pages)} crawled, {errors} errors",
        f"Depth: {max_depth}\n",
        "## Pages\n",
    ]
    for p in pages:
        lines.append(f"- [{p['title']}]({p['file']}) — depth {p['depth']}, {p['size']:,} chars")
        lines.append(f"  {p['url']}")
    index_path.write_text("\n".join(lines) + "\n")

    total_size = sum(p["size"] for p in pages)
    print(f"\nCrawl complete!")
    print(f"Pages: {len(pages)} crawled, {errors} errors")
    print(f"Index: {index_path}")
    print(f"Pages dir: {pages_dir}")
    print(f"Total content: {total_size:,} chars")


def main():
    parser = argparse.ArgumentParser(description="Crawl documentation sites to local markdown files")
    parser.add_argument("--output-dir", default=".crawl", help="Output directory (default: .crawl)")
    sub = parser.add_subparsers(dest="command", required=True)

    page_cmd = sub.add_parser("page", help="Crawl a single page")
    page_cmd.add_argument("url", help="URL to crawl")

    site_cmd = sub.add_parser("site", help="Deep crawl a documentation site")
    site_cmd.add_argument("url", help="Starting URL")
    site_cmd.add_argument("--depth", type=int, default=3, help="Max depth (default: 3)")
    site_cmd.add_argument("--max-pages", type=int, default=50, help="Max pages (default: 50)")

    args = parser.parse_args()

    if args.command == "page":
        asyncio.run(crawl_page(args.url, args.output_dir))
    elif args.command == "site":
        depth = max(1, min(10, args.depth))
        max_pages = max(1, min(500, args.max_pages))
        asyncio.run(crawl_site(args.url, depth, max_pages, args.output_dir))


if __name__ == "__main__":
    main()
