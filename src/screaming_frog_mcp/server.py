"""MCP server for Screaming Frog SEO Spider crawl analysis."""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Screaming Frog SEO")

# ---------------------------------------------------------------------------
# Crawl cache: keeps loaded crawls in memory to avoid reloading on every call
# ---------------------------------------------------------------------------
_crawl_cache: dict[str, Any] = {}


def _get_crawl(crawl_path: str) -> Any:
    """Load a crawl from cache or from disk."""
    from screamingfrog import Crawl

    path = str(Path(crawl_path).expanduser().resolve())
    if path not in _crawl_cache:
        _crawl_cache[path] = Crawl.load(path)
    return _crawl_cache[path]


def _rows_to_dicts(rows, limit: int = 200) -> list[dict]:
    """Convert crawl result rows to a list of dicts, with a row limit."""
    results = []
    for i, row in enumerate(rows):
        if i >= limit:
            break
        if isinstance(row, dict):
            results.append(row)
        elif hasattr(row, "__dict__"):
            results.append({k: v for k, v in row.__dict__.items() if not k.startswith("_")})
        elif hasattr(row, "items"):
            results.append(dict(row.items()))
        else:
            results.append({"value": str(row)})
    return results


def _safe_json(obj: Any) -> str:
    """Serialize to JSON, converting non-serializable values to strings."""
    def default(o: Any) -> Any:
        return str(o)
    return json.dumps(obj, default=default, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def load_crawl(crawl_path: str) -> str:
    """Load a Screaming Frog crawl file and return basic info.

    Supports: .dbseospider, .seospider, .duckdb, .db, CSV export directories.

    Args:
        crawl_path: Path to the crawl file or directory.
    """
    try:
        crawl = _get_crawl(crawl_path)
        info = {"status": "loaded", "path": crawl_path}
        if hasattr(crawl, "tabs"):
            info["available_tabs"] = len(crawl.tabs) if not callable(crawl.tabs) else "unknown"
        return _safe_json(info)
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def crawl_summary(crawl_path: str) -> str:
    """Get a high-level summary of the crawl (total URLs, status codes, etc.).

    Args:
        crawl_path: Path to the crawl file.
    """
    try:
        crawl = _get_crawl(crawl_path)
        summary = crawl.summary()
        if isinstance(summary, dict):
            return _safe_json(summary)
        return str(summary)
    except Exception as e:
        return _safe_json({"error": str(e)})


@mcp.tool()
def get_pages(
    crawl_path: str,
    status_code: int | None = None,
    indexable: bool | None = None,
    search: str | None = None,
    section: str | None = None,
    fields: str | None = None,
    limit: int = 100,
) -> str:
    """Query pages from the crawl with optional filters.

    Args:
        crawl_path: Path to the crawl file.
        status_code: Filter by HTTP status code (e.g. 404, 301, 200).
        indexable: Filter by indexability (true/false).
        search: Full-text search term across page fields.
        section: URL path prefix to scope the query (e.g. "/blog").
        fields: Comma-separated list of fields to return (e.g. "Address,Status Code,Title 1").
        limit: Max number of results (default 100).
    """
    try:
        crawl = _get_crawl(crawl_path)
        query = crawl.section(section) if section else crawl
        pages = query.pages()

        if status_code is not None:
            pages = pages.filter(status_code=status_code)
        if indexable is not None:
            pages = pages.filter(indexable=indexable)
        if search:
            pages = pages.search(search)
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            pages = pages.select(*field_list)

        rows = _rows_to_dicts(pages, limit=limit)
        return _safe_json({"count": len(rows), "pages": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def get_links(
    crawl_path: str,
    direction: str = "in",
    url: str | None = None,
    section: str | None = None,
    limit: int = 100,
) -> str:
    """Query inbound or outbound links from the crawl.

    Args:
        crawl_path: Path to the crawl file.
        direction: "in" for inbound links, "out" for outbound links.
        url: Specific URL to get links for. If omitted, returns sitewide links.
        section: URL path prefix to scope the query.
        limit: Max number of results (default 100).
    """
    try:
        crawl = _get_crawl(crawl_path)
        if url:
            links = crawl.inlinks(url) if direction == "in" else crawl.outlinks(url)
        else:
            query = crawl.section(section) if section else crawl
            links = query.links(direction)

        rows = _rows_to_dicts(links, limit=limit)
        return _safe_json({"count": len(rows), "direction": direction, "links": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def broken_links_report(crawl_path: str, limit: int = 200) -> str:
    """Get a report of all broken internal links with inlink counts.

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.broken_links_report(), limit=limit)
        return _safe_json({"count": len(rows), "broken_links": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def title_meta_audit(crawl_path: str, limit: int = 200) -> str:
    """Audit pages for missing or problematic titles and meta descriptions.

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.title_meta_audit(), limit=limit)
        return _safe_json({"count": len(rows), "issues": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def indexability_audit(crawl_path: str, limit: int = 200) -> str:
    """Find non-indexable pages with reasons (noindex, canonical, etc.).

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.indexability_audit(), limit=limit)
        return _safe_json({"count": len(rows), "non_indexable": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def redirect_chains_report(crawl_path: str, min_hops: int = 2, limit: int = 200) -> str:
    """Find redirect chains exceeding a minimum number of hops.

    Args:
        crawl_path: Path to the crawl file.
        min_hops: Minimum number of hops to report (default 2).
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.redirect_chain_report(min_hops=min_hops), limit=limit)
        return _safe_json({"count": len(rows), "min_hops": min_hops, "chains": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def canonical_issues_report(crawl_path: str, limit: int = 200) -> str:
    """Find pages with canonical tag issues.

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.canonical_issues_report(), limit=limit)
        return _safe_json({"count": len(rows), "issues": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def hreflang_issues_report(crawl_path: str, limit: int = 200) -> str:
    """Find hreflang implementation issues.

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.hreflang_issues_report(), limit=limit)
        return _safe_json({"count": len(rows), "issues": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def orphan_pages_report(crawl_path: str, only_indexable: bool = True, limit: int = 200) -> str:
    """Find orphan pages (no internal links pointing to them).

    Args:
        crawl_path: Path to the crawl file.
        only_indexable: Only report indexable orphan pages (default true).
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.orphan_pages_report(only_indexable=only_indexable), limit=limit)
        return _safe_json({"count": len(rows), "orphan_pages": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def security_issues_report(crawl_path: str, limit: int = 200) -> str:
    """Find security issues (mixed content, HTTP pages, etc.).

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.security_issues_report(), limit=limit)
        return _safe_json({"count": len(rows), "issues": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def redirect_issues_report(crawl_path: str, limit: int = 200) -> str:
    """Find redirect-related issues (loops, long chains, etc.).

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.redirect_issues_report(), limit=limit)
        return _safe_json({"count": len(rows), "issues": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def nofollow_inlinks_report(crawl_path: str, limit: int = 200) -> str:
    """Find pages receiving nofollow inbound links.

    Args:
        crawl_path: Path to the crawl file.
        limit: Max number of results (default 200).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.nofollow_inlinks_report(), limit=limit)
        return _safe_json({"count": len(rows), "nofollow_inlinks": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def compare_crawls(crawl_path_new: str, crawl_path_old: str) -> str:
    """Compare two crawls and return the differences (new vs old).

    Args:
        crawl_path_new: Path to the newer crawl file.
        crawl_path_old: Path to the older crawl file.
    """
    try:
        new = _get_crawl(crawl_path_new)
        old = _get_crawl(crawl_path_old)
        diff = new.compare(old)

        result: dict[str, Any] = {}
        if hasattr(diff, "summary"):
            summary = diff.summary()
            result["summary"] = summary if isinstance(summary, dict) else str(summary)
        if hasattr(diff, "status_changes"):
            changes = []
            for c in diff.status_changes[:50]:
                changes.append({
                    "url": getattr(c, "url", str(c)),
                    "old_status": getattr(c, "old_status", None),
                    "new_status": getattr(c, "new_status", None),
                })
            result["status_changes"] = changes
        return _safe_json(result)
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def query_tab(crawl_path: str, tab_name: str, limit: int = 100) -> str:
    """Query any available tab from the crawl by name.

    Use list_tabs first to see available tab names.

    Args:
        crawl_path: Path to the crawl file.
        tab_name: Name of the tab to query (e.g. "response_codes_all", "Page Titles:All").
        limit: Max number of results (default 100).
    """
    try:
        crawl = _get_crawl(crawl_path)
        rows = _rows_to_dicts(crawl.tab(tab_name), limit=limit)
        return _safe_json({"tab": tab_name, "count": len(rows), "rows": rows})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def list_tabs(crawl_path: str) -> str:
    """List all available tabs in the crawl.

    Args:
        crawl_path: Path to the crawl file.
    """
    try:
        crawl = _get_crawl(crawl_path)
        tabs = crawl.tabs
        if callable(tabs):
            tabs = tabs()
        return _safe_json({"tabs": list(tabs) if not isinstance(tabs, list) else tabs})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def list_crawls(project_root: str | None = None) -> str:
    """Discover available Screaming Frog crawls on this machine.

    Args:
        project_root: Optional root directory to search for crawls.
    """
    try:
        from screamingfrog import list_crawls as sf_list_crawls

        kwargs = {}
        if project_root:
            kwargs["project_root"] = project_root
        crawls = sf_list_crawls(**kwargs)
        results = []
        for info in crawls:
            entry = {}
            for attr in ("db_id", "url", "urls_crawled", "path"):
                if hasattr(info, attr):
                    entry[attr] = str(getattr(info, attr))
            results.append(entry)
        return _safe_json({"crawls": results})
    except Exception as e:
        return _safe_json({"error": str(e), "traceback": traceback.format_exc()})


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
