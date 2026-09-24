from ddgs import DDGS
from urllib.parse import urlparse
import re

def _queries(profile, opportunity_type, location, work_mode, funding, custom_keywords):
    fields = profile.get("target_fields", [])
    field_text = " OR ".join(fields[:8]) if fields else "civil engineering OR urban planning OR GIS OR smart cities"
    extra = custom_keywords.strip()
    if extra:
        field_text += " OR " + extra

    location_text = "" if location == "Worldwide" else location

    queries = []

    if opportunity_type in ("Jobs", "Jobs + PhD / Scholarships"):
        queries.extend([
            f'({field_text}) jobs {location_text} {work_mode} {funding}',
            f'({field_text}) vacancy careers {location_text} {work_mode}',
            f'({field_text}) remote jobs international',
        ])

    if opportunity_type in ("Fully Funded PhD / Scholarships", "Jobs + PhD / Scholarships"):
        queries.extend([
            f'PhD fully funded scholarship {field_text} {location_text}',
            f'funded PhD research position {field_text} {location_text}',
            f'PhD scholarship smart cities urban planning AI GIS {location_text}',
        ])

    return [q.replace("  ", " ").strip() for q in queries]

def _blocked(item, location, exclude_municipal):
    text = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        item.get("organization", ""),
    ]).lower()

    if exclude_municipal and location == "Pakistan":
        blocked_terms = [
            "municipal officer", "tmo", "town municipal",
            "municipal committee", "local government officer",
        ]
        if any(term in text for term in blocked_terms):
            return True
    return False

def _domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def search_web(query, max_results=8):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception:
        return []

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
    raw = []
    seen = set()

    for query in _queries(
        profile, opportunity_type, location, work_mode, funding, custom_keywords
    ):
        for result in search_web(query, max_results=8):
            url = result.get("href") or result.get("url") or ""
            title = result.get("title", "")
            if not url or not title:
                continue
            key = url.split("#")[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            raw.append({
                "title": title,
                "url": url,
                "summary": result.get("body", ""),
                "domain": _domain(url),
            })

    if not raw:
        return []

    # Keep prompts manageable.
    raw = raw[:max_results * 2]

    profile_text = str(profile)
    candidates = "\n\n".join(
        f"ID:{i}\nTITLE:{x['title']}\nURL:{x['url']}\nSNIPPET:{x['summary']}"
        for i, x in enumerate(raw)
    )

    system = """
You are a career opportunity analyst. Analyze search-result candidates against the
candidate's profile. Do not invent facts. A match score is a transparent fit estimate,
not a promise of employment or admission.

Return JSON:
{
  "results": [
    {
      "id": 0,
      "organization": "",
      "location": "",
      "type": "Job|PhD|Scholarship|Research",
      "funding": "",
      "deadline": "",
      "summary": "",
      "match_score": 0,
      "match_reasons": ["", ""]
    }
  ]
}

Only include plausible opportunities. Prefer official university/employer pages.
If a deadline is not visible, use "Not stated".
"""
    user = f"""
Candidate profile:
{profile_text}

Requested opportunity type: {opportunity_type}
Location: {location}
Work mode: {work_mode}
Funding: {funding}

Candidates:
{candidates}
"""

    try:
        analysis = ai.json(system, user)
    except Exception:
        analysis = {"results": []}

    output = []
    for a in analysis.get("results", []):
        try:
            idx = int(a.get("id"))
            source = raw[idx]
        except Exception:
            continue

        item = {
            "title": source["title"],
            "url": source["url"],
            "domain": source["domain"],
            "organization": a.get("organization", ""),
            "location": a.get("location", ""),
            "type": a.get("type", "Opportunity"),
            "funding": a.get("funding", ""),
            "deadline": a.get("deadline", ""),
            "summary": a.get("summary", source["summary"]),
            "match_score": max(0, min(100, int(a.get("match_score", 0)))),
            "match_reasons": a.get("match_reasons", []),
        }

        if not _blocked(item, location, exclude_municipal):
            output.append(item)

    output.sort(key=lambda x: x["match_score"], reverse=True)
    return output[:max_results]
