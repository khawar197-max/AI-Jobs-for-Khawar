from ddgs import DDGS


def search_opportunities(
    profile,
    opportunity_type,
    location,
    work_mode,
    funding,
    custom_keywords,
    max_results,
    exclude_municipal,
    ai,
):

    results = []

    queries = [
        '"civil engineering" jobs',
        '"urban planning" jobs',
        '"GIS" jobs',
        '"smart cities" jobs',
        '"geotechnical engineering" jobs',
    ]

    if "PhD" in opportunity_type or "Scholarships" in opportunity_type:
        queries = [
            '"civil engineering" PhD "fully funded"',
            '"urban planning" PhD "fully funded"',
            '"GIS" PhD "fully funded"',
            '"smart cities" PhD "fully funded"',
        ]

    for query in queries:

        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    max_results=5
                )

                for r in search_results:

                    title = r.get("title", "")
                    url = r.get("href", "")
                    description = r.get("body", "")

                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "organization": "Not stated",
                            "location": location,
                            "type": opportunity_type,
                            "funding": funding,
                            "deadline": "Not stated",
                            "summary": description,
                            "match_score": 0,
                            "match_reasons": [
                                "Found through web search."
                            ]
                        })

        except Exception as e:
            print("Search error:", e)

    # Remove duplicate URLs
    unique = {}

    for item in results:
        unique[item["url"]] = item

    results = list(unique.values())

    return results[:max_results]
