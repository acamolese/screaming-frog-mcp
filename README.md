# Screaming Frog MCP Server

MCP server that exposes Screaming Frog SEO Spider crawl data as tool calls for any MCP-compatible AI assistant.

Built on top of the [screamingfrog](https://github.com/Amaculus/screaming-frog-api) Python library.

## Requirements

- Python 3.10+
- Java runtime (for `.dbseospider` files with Derby backend)
- Screaming Frog SEO Spider installed (optional, for `.seospider` conversion)

## Installation

```bash
git clone https://github.com/acamolese/screaming-frog-mcp.git
cd screaming-frog-mcp
pip install -e .
```

## Configuration

Add to your MCP client settings:

```json
{
  "mcpServers": {
    "screaming-frog-seo": {
      "command": "screaming-frog-mcp"
    }
  }
}
```

## Available tools

| Tool | Descrizione |
|------|-------------|
| `load_crawl` | Carica un file di crawl |
| `crawl_summary` | Sommario del crawl |
| `get_pages` | Query pagine con filtri (status code, indicizzabilita, ricerca testo, sezione) |
| `get_links` | Query link in ingresso/uscita |
| `broken_links_report` | Report link rotti |
| `title_meta_audit` | Audit title e meta description |
| `indexability_audit` | Pagine non indicizzabili |
| `redirect_chains_report` | Catene di redirect |
| `canonical_issues_report` | Problemi canonical |
| `hreflang_issues_report` | Problemi hreflang |
| `orphan_pages_report` | Pagine orfane |
| `security_issues_report` | Problemi di sicurezza |
| `redirect_issues_report` | Problemi redirect |
| `nofollow_inlinks_report` | Link nofollow in ingresso |
| `compare_crawls` | Confronto tra due crawl |
| `query_tab` | Accesso a qualsiasi tab del crawl |
| `list_tabs` | Elenco tab disponibili |
| `list_crawls` | Scopri crawl disponibili sulla macchina |

### Formati supportati

- `.dbseospider` (Derby, formato nativo DB-mode)
- `.seospider` (progetto Screaming Frog, richiede CLI installata)
- `.duckdb` (cache DuckDB)
- `.db` (SQLite legacy)
- Directory di export CSV

## Licenza

MIT
