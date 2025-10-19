#!/usr/bin/env python3
"""
google_scholar_scraper.py
=========================

This script automates the retrieval of all publications for a given Google
Scholar author.  By supplying the URL of an author's Google Scholar profile
(`https://scholar.google.com/citations?user=<ID>&hl=<lang>`), the script
parses the underlying `user` parameter to obtain the unique author ID and
leverages the `scholarly` Python package to fetch the author's metadata and
their entire publication list.  Each publication is then filled out to
retrieve detailed bibliographic information such as the title, authors,
journal/venue, publication year, abstract, number of citations, and links
to the original work.  The final output is written as a JSON document with
a unified structure consisting of author metadata and a list of article
records.

The `scholarly` library was chosen because it provides programmatic access
to Google Scholar without requiring official API keys and can return
detailed publication information.  According to the project's
documentation, it allows retrieval of author and publication information
from Google Scholar "in a friendly, Pythonic way without having to solve
CAPTCHAs"【417558673383529†L94-L98】 and does not require an API key【149657658920553†L69-L76】.  The
script optionally supports the use of free or paid proxies via
`ProxyGenerator` to mitigate the risk of IP blocks (which the
documentation warns can occur when making certain types of queries
【417558673383529†L186-L189】).

Usage example::

    python3 google_scholar_scraper.py \
        "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en" \
        --output jeremy_crenshaw.json

The above command will create a JSON file named ``jeremy_crenshaw.json``
containing the author information and a list of all publications by the
author represented by the supplied URL.

Notes
-----
* Running this script repeatedly against Google Scholar may eventually
  trigger anti-bot measures.  To reduce the likelihood of being blocked,
  enable the ``--use-proxy`` option which configures `scholarly` to use
  free proxies or other proxy services available via `ProxyGenerator`.
* If a publication does not include certain bibliographic fields (for
  example, page numbers or abstract), those entries will be set to
  ``None`` in the output.

"""

import argparse
import json
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any

from scholarly import scholarly, ProxyGenerator  # type: ignore


def extract_author_id(url: str) -> Optional[str]:
    """Extract the Google Scholar author ID from a profile URL.

    Google Scholar profile URLs include a ``user`` query parameter whose
    value uniquely identifies the author.  For example, in the URL
    ``https://scholar.google.com/citations?user=Smr99uEAAAAJ&hl=en`` the
    author ID is ``Smr99uEAAAAJ``.  This helper parses the query string
    and returns the value associated with ``user``.  If the parameter is
    not present, ``None`` is returned.

    Parameters
    ----------
    url : str
        A Google Scholar author profile URL.

    Returns
    -------
    Optional[str]
        The extracted author ID if available, otherwise ``None``.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    user_list = params.get("user")
    if user_list:
        return user_list[0]
    return None


def setup_proxy(method: str = "free", scraperapi_key: Optional[str] = None) -> None:
    """Configure proxies for the `scholarly` library.

    `scholarly` supports several proxy backends through the
    ``ProxyGenerator`` class.  This function sets up the desired proxy
    method based on user input.  If no proxy is requested, this function
    does nothing.  When using a proxy, `scholarly.use_proxy()` must be
    invoked exactly once per session.

    Parameters
    ----------
    method : str
        The proxy method to use.  Supported options include ``"free"``,
        ``"scraperapi"``, ``"tor"``, and ``"none"``.  The ``"free"``
        option uses a pool of free proxies discovered by `scholarly` and
        may be unstable but does not require credentials.  ``"scraperapi"``
        requires a valid API key (provided via ``scraperapi_key``).  The
        ``"tor"`` option attempts to launch an internal Tor client; note
        that Tor support may depend on the local environment.  ``"none"``
        skips proxy configuration and relies on the default IP address.

    scraperapi_key : Optional[str]
        API key for the ``scraperapi`` proxy method.  Ignored if
        ``method`` is not ``"scraperapi"``.
    """
    if method == "none":
        return
    pg = ProxyGenerator()
    if method == "free":
        # Use a pool of free proxies
        pg.FreeProxies()
    elif method == "scraperapi":
        if not scraperapi_key:
            raise ValueError(
                "`scraperapi_key` must be provided when using the scraperapi proxy."
            )
        pg.ScraperAPI(scraperapi_key)
    elif method == "tor":
        # Launch an internal Tor instance using default ports.  Users may
        # customise the ports as needed.  Tor must be installed on the
        # system for this to work.
        pg.Tor_Internal()
    else:
        raise ValueError(f"Unsupported proxy method: {method}")
    # Register the proxy with scholarly
    scholarly.use_proxy(pg)


def scrape_author(url: str, use_proxy: bool = False, proxy_method: str = "free", scraperapi_key: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve an author's profile and all publications from Google Scholar.

    This function orchestrates the scraping process.  It extracts the
    author ID from the provided URL, configures proxies if requested,
    retrieves the author's basic details and list of publications, fills
    each publication with additional bibliographic information, and
    assembles a unified data structure representing the author and their
    works.

    Parameters
    ----------
    url : str
        The Google Scholar author profile URL.
    use_proxy : bool, optional
        Whether to enable proxy usage.  Defaults to ``False``.
    proxy_method : str, optional
        The proxy backend to use when ``use_proxy`` is true.  See
        :func:`setup_proxy` for valid options.  Defaults to ``"free"``.
    scraperapi_key : Optional[str], optional
        API key used when ``proxy_method`` is ``"scraperapi"``.  Defaults
        to ``None``.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing author information under the key
        ``"author"`` and a list of publication dictionaries under
        ``"articles"``.

    Raises
    ------
    ValueError
        If the author ID cannot be extracted from the URL or if proxy
        configuration fails.
    """
    author_id = extract_author_id(url)
    if not author_id:
        raise ValueError(
            f"Failed to parse author ID from URL: {url}. Ensure the URL contains a 'user' parameter."
        )

    # Configure proxy if requested
    if use_proxy:
        setup_proxy(proxy_method, scraperapi_key)

    # Search for the author by ID.  `search_author_id` returns a lightly
    # populated Author object that must be filled to obtain details and
    # publications【149657658920553†L121-L134】.
    author_obj = scholarly.search_author_id(author_id)
    # Fill the author object with basic info and list of publications
    author_filled = scholarly.fill(author_obj, sections=["basics", "publications"])

    # Assemble author-level metadata
    author_data: Dict[str, Any] = {
        "scholar_id": author_filled.get("scholar_id"),
        "name": author_filled.get("name"),
        "affiliation": author_filled.get("affiliation"),
        "email_domain": author_filled.get("email_domain"),
        "interests(label)": author_filled.get("interests"),
        "citedby": author_filled.get("citedby"),
        "citedby5y": author_filled.get("citedby5y"),
    }

    articles = []
    publications = author_filled.get("publications", [])
    # Add total publication count to author data
    author_data["total_publications"] = len(publications)

    for pub in publications:
        try:
            # Fill each publication to retrieve detailed information【149657658920553†L214-L218】.
            pub_filled = scholarly.fill(pub)
        except Exception as exc:
            # If filling fails (e.g., due to network issues), record minimal info
            pub_filled = pub
            pub_filled["_fill_error"] = str(exc)

        bib: Dict[str, Any] = pub_filled.get("bib", {}) if isinstance(pub_filled, dict) else {}
        article_entry: Dict[str, Any] = {
            # Some IDs (e.g., citation_id) are not directly exposed by `scholarly`.
            "title": bib.get("title"),
            "authors": bib.get("author"),
            "journal": bib.get("venue"),
            "year": bib.get("pub_year"),
            "abstract": bib.get("abstract"),
            "pages": bib.get("pages"),
            "num_citations": pub_filled.get("num_citations"),
            "cited_by_url": pub_filled.get("citedby_url"),
            "pub_url": pub_filled.get("pub_url"),
            "eprint_url": pub_filled.get("eprint_url"),
            "url_scholarbib": pub_filled.get("url_scholarbib"),
            "source": pub_filled.get("source"),
        }
        # Preserve underlying author_id list for multi-author papers
        author_ids = pub_filled.get("author_id")
        if author_ids:
            article_entry["author_ids"] = author_ids
        # If there was an error during filling, include it for debugging
        if "_fill_error" in pub_filled:
            article_entry["fill_error"] = pub_filled["_fill_error"]
        articles.append(article_entry)

    return {"author": author_data, "articles": articles}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape a Google Scholar author's profile and publications into JSON."
    )
    parser.add_argument(
        "url",
        help="Google Scholar author profile URL (e.g. https://scholar.google.com/citations?user=ID&hl=en)",
    )
    parser.add_argument(
        "--output",
        default="author_publications.json",
        help="Path to the output JSON file. Defaults to 'author_publications.json'.",
    )
    parser.add_argument(
        "--use-proxy",
        action="store_true",
        help="Enable use of proxies to reduce risk of Google Scholar blocking requests.",
    )
    parser.add_argument(
        "--proxy-method",
        choices=["free", "scraperapi", "tor", "none"],
        default="free",
        help="Proxy backend to use when --use-proxy is specified."
             " 'free' uses public proxies, 'scraperapi' uses a paid proxy,"
             " 'tor' launches an internal Tor instance, and 'none' disables proxies.",
    )
    parser.add_argument(
        "--scraperapi-key",
        help="API key for scraperapi (required if --proxy-method=scraperapi).",
    )

    args = parser.parse_args()

    data = scrape_author(
        url=args.url,
        use_proxy=args.use_proxy,
        proxy_method=args.proxy_method,
        scraperapi_key=args.scraperapi_key,
    )

    # Write the result to the specified output file
    with open(args.output, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

    print(f"Scraped data for author saved to {args.output}")


if __name__ == "__main__":
    main()