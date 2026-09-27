from ddgs import DDGS
from urllib.parse import urlparse


def build_queries(
    opportunity_type,
    location,
    work_mode,
    funding,
    custom_keywords,
    career_area,
):
    """
    Build multiple targeted searches instead of relying on only
    Civil Engineering / Gulf searches.
    """

    career_queries = {
        "Civil Engineering": [
            '"civil engineer" jobs',
            '"site engineer" civil jobs',
            '"civil engineering" vacancies',
        ],
        "Geotechnical Engineering": [
            '"geotechnical engineer" jobs',
            '"geotechnical engineering" vacancies',
        ],
        "Highway & Transportation": [
            '"highway engineer" jobs',
            '"transportation engineer" jobs',
            '"traffic engineer" jobs',
        ],
        "Urban Planning": [
            '"urban planner" jobs',
            '"urban planning" jobs',
            '"town planner" jobs',
        ],
        "GIS": [
            '"GIS analyst" jobs',
            '"GIS specialist" jobs',
            '"GIS engineer" jobs',
        ],
        "Smart Cities": [
            '"smart city" jobs',
            '"smart cities" jobs',
            '"urban technology" jobs',
        ],
        "Project Management": [
            '"project coordinator" jobs',
            '"project officer" jobs',
            '"project management" jobs',
        ],
        "Administration & Operations": [
            '"administrative officer" jobs',
            '"operations officer" jobs',
            '"administration" jobs',
        ],
        "Data Entry": [
            '"data entry" jobs',
            '"data entry specialist" jobs',
            '"data entry operator" jobs',
        ],
        "Virtual Assistant": [
            '"virtual assistant" jobs',
            '"remote virtual assistant" jobs',
            '"virtual assistant" freelance',
        ],
        "Digital Marketing": [
            '"digital marketing" jobs',
            '"digital marketing assistant" jobs',
            '"digital marketing specialist" jobs',
        ],
        "Social Media Management": [
            '"social media manager" jobs',
            '"social media specialist" jobs',
            '"social media management" jobs',
        ],
        "Content Management": [
            '"content manager" jobs',
            '"content specialist" jobs',
            '"content management" jobs',
        ],
        "AI & Automation": [
            '"AI assistant" jobs',
            '"AI automation" jobs',
            '"AI operations" jobs',
            '"AI specialist" jobs',
        ],
        "Research": [
            '"research assistant" jobs',
            '"research associate" jobs',
            '"research officer" jobs',
        ],
    }

    # If user selected "All Career Areas"
    if career_area == "All Career Areas":
        selected_queries = []

        for category_queries in career_queries.values():
            selected_queries.extend(category_queries[:2])

    else:
        selected_queries = career_queries.get(
            career_area,
            ['"civil engineering" jobs']
        )

    # Location
    location_terms = {
        "Worldwide": "",
        "Pakistan": "Pakistan",
        "Europe": "Europe",
        "USA & Canada": '"USA" OR "Canada"',
        "Gulf / Middle East": '"Saudi Arabia" OR UAE OR Qatar OR Oman OR Bahrain OR Kuwait',
        "Asia-Pacific": '"Australia" OR "New Zealand" OR Singapore OR Malaysia',
    }

    location_term = location_terms.get(location, "")

    # Work mode
    work_terms = {
        "Any": "",
        "Remote": "remote",
        "On-site": '"on-site"',
        "Hybrid": "hybrid",
    }

    work_term = work_terms.get(work_mode, "")

    # Funding
    funding_term = ""

    if funding == "Fully funded":
        funding_term = '"fully funded"'
    elif funding == "Funded / stipend":
        funding_term = '"funded" OR stipend'
    elif funding == "Scholarship":
        funding_term = '"scholarship"'

    final_queries = []

    for base_query in selected_queries:

        parts = [base_query]

        if location_term:
            parts.append(location_term)

        if work_term:
            parts.append(work_term)

        if funding_term:
            parts.append(funding_term)

        if custom_keywords.strip():
            parts.append(custom_keywords.strip())

        final_queries.append(" ".join(parts))

    # PhD / Scholarship searches
    if "PhD" in opportunity_type or "Scholarships" in opportunity_type:

        phd_queries = [
            '"civil engineering" PhD "fully funded"',
            '"geotechnical engineering" PhD "fully funded"',
            '"urban planning" PhD "fully funded"',
            '"GIS" PhD "fully funded"',
            '"smart cities" PhD "fully funded"',
            '"transportation" PhD "fully funded"',
            '"urban studies" PhD "fully funded"',
        ]

        for q in phd_queries:

            parts = [q]

            if location_term:
                parts.append(location_term)

            if funding_term:
                parts.append(funding_term)

            if custom_keywords.strip():
                parts.append(custom_keywords.strip())

            final_queries.append(" ".join(parts))

    return final_queries


def extract_domain(url):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


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
    career_area="All Career Areas",
):

    results = []

    queries = build_queries(
        opportunity_type=opportunity_type,
        location=location,
        work_mode=work_mode,
        funding=funding,
        custom_keywords=custom_keywords,
        career_area=career_area,
    )

    # Search more results per query so that final results are not limited.
    results_per_query = 8

    for query in queries:

        try:

            with DDGS() as ddgs:

                search_results = ddgs.text(
                    query,
                    max_results=results_per_query
                )

                for r in search_results:

                    title = r.get("title", "")
                    url = r.get("href", "")
                    description = r.get("body", "")

                    if not title or not url:
                        continue

                    # Optional municipal exclusion
                    if exclude_municipal:

                        text_to_check = (
                            title + " " + description
                        ).lower()

                        municipal_words = [
                            "municipal officer",
                            "municipal committee",
                            "town municipal",
                            "local government",
                            "municipal corporation",
                        ]

                        if (
                            location == "Pakistan"
                            and any(
                                word in text_to_check
                                for word in municipal_words
                            )
                        ):
                            continue

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
                            "Found through targeted web search."
                        ],
                        "career_area": career_area,
                        "source": extract_domain(url),
                    })

        except Exception as e:

            print("Search error:", e)

    # Remove duplicate URLs
    unique = {}

    for item in results:

        url = item.get("url", "").strip()

        if url:
            unique[url] = item

    results = list(unique.values())

    # Remove obvious search/category pages
    cleaned = []

    unwanted_words = [
        "login",
        "signup",
        "register",
        "privacy",
        "terms",
        "cookie",
    ]

    for item in results:

        combined = (
            item.get("title", "") + " " +
            item.get("url", "")
        ).lower()

        if any(word in combined for word in unwanted_words):
            continue

        cleaned.append(item)

    results = cleaned

    # Basic keyword matching before displaying results.
    # This does not replace AI matching but helps prioritize relevant jobs.
    profile_text = str(profile).lower()

    for item in results:

        text = (
            item.get("title", "") + " " +
            item.get("summary", "")
        ).lower()

        score = 0
        reasons = []

        keywords = [
            "civil",
            "engineering",
            "geotechnical",
            "highway",
            "transportation",
            "urban planning",
            "gis",
            "smart city",
            "project",
            "administration",
            "operations",
            "data entry",
            "virtual assistant",
            "digital marketing",
            "social media",
            "content",
            "ai",
            "research",
        ]

        for keyword in keywords:

            if keyword in text:

                if keyword in profile_text:
                    score += 8
                    reasons.append(
                        f"Matches your profile through {keyword}."
                    )
                else:
                    score += 2

        # Work mode boost
        if work_mode == "Remote" and "remote" in text:
            score += 10
            reasons.append("Remote opportunity.")

        if work_mode == "Hybrid" and "hybrid" in text:
            score += 5
            reasons.append("Hybrid opportunity.")

        item["match_score"] = min(score, 99)

        if reasons:
            item["match_reasons"] = reasons[:5]

    # Sort highest matching opportunities first
    results.sort(
        key=lambda x: x.get("match_score", 0),
        reverse=True
    )

    return results[:max_results]
