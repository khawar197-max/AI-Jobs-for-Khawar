```python
from ddgs import DDGS
from urllib.parse import urlparse
import re
import time


# ---------------------------------------------------------
# 1. BUILD SEARCH QUERIES
# ---------------------------------------------------------

def _queries(profile, opportunity_type, location, work_mode, funding, custom_keywords):

    fields = profile.get("target_fields", [])

    if not fields:
        fields = [
            "civil engineering",
            "urban planning",
            "GIS",
            "smart cities",
            "geotechnical engineering",
        ]

    # Add custom keywords if provided
    if custom_keywords and custom_keywords.strip():
        fields = fields + [custom_keywords.strip()]

    queries = []

    # JOB SEARCH
    if opportunity_type in ("Jobs", "Jobs + PhD / Scholarships"):

        for field in fields[:6]:
            queries.append(f'"{field}" jobs')

        if work_mode == "Remote":
            for field in fields[:4]:
                queries.append(f'"{field}" remote jobs')

        elif work_mode == "Hybrid":
            for field in fields[:4]:
                queries.append(f'"{field}" hybrid jobs')

        elif work_mode == "On-site":
            for field in fields[:4]:
                queries.append(f'"{field}" on-site jobs')

    # PHD / SCHOLARSHIP SEARCH
    if opportunity_type in (
        "Fully Funded PhD / Scholarships",
        "Jobs + PhD / Scholarships",
    ):

        for field in fields[:6]:
            queries.append(f'"{field}" PhD "fully funded"')

        for field in fields[:4]:
            queries.append(f'"{field}" funded PhD')

        queries.append('"urban planning" PhD scholarship')
        queries.append('"smart cities" PhD scholarship')
        queries.append('"GIS" PhD scholarship')

    # Remove duplicates
    queries = list(dict.fromkeys(queries))

    return queries


# ---------------------------------------------------------
# 2. BLOCK UNWANTED RESULTS
# ---------------------------------------------------------

def _blocked(item, location, exclude_municipal):

    text = " ".join([
        str(item.get("title", "")),
        str(item.get("summary", "")),
        str(item.get("organization", "")),
    ]).lower()

    if exclude_municipal and location == "Pakistan":

        blocked_terms = [
            "municipal officer",
            "tmo",
            "town municipal",
            "municipal committee",
            "local government officer",
        ]

        if any(term in text for term in blocked_terms):
            return True

    return False


# ---------------------------------------------------------
# 3. GET DOMAIN
# ---------------------------------------------------------

def _domain(url):

    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


# ---------------------------------------------------------
# 4. DDGS SEARCH
# ---------------------------------------------------------

def search_web(query, max_results=8):

    try:

        print(f"DDGS QUERY: {query}")

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results,
            )

            output = []

            for result in results:

                if not isinstance(result, dict):
                    continue

                title = str(result.get("title", "")).strip()
                url = str(
                    result.get("href", "")
                    or result.get("url", "")
                ).strip()

                body = str(
                    result.get("body", "")
                    or result.get("snippet", "")
                ).strip()

                if not title or not url:
                    continue

                output.append({
                    "title": title,
                    "href": url,
                    "body": body,
                })

            print(f"DDGS RESULTS: {len(output)}")

            return output

    except Exception as e:

        print("DDGS SEARCH ERROR:", repr(e))

        return []


# ---------------------------------------------------------
# 5. FALLBACK RAW RESULTS
# ---------------------------------------------------------

def _make_fallback_results(raw, max_results):

    output = []

    for item in raw[:max_results]:

        output.append({
            "title": item.get("title", "Untitled opportunity"),
            "url": item.get("url", ""),
            "domain": item.get("domain", ""),
            "organization": "Not stated",
            "location": "Not stated",
            "type": "Opportunity",
            "funding": "Not stated",
            "deadline": "Not stated",
            "summary": item.get("summary", ""),
            "match_score": 0,
            "match_reasons": [
                "Found through web search.",
                "AI analysis was unavailable, so this result is shown as a raw opportunity."
            ],
        })

    return output


# ---------------------------------------------------------
# 6. MAIN SEARCH FUNCTION
# ---------------------------------------------------------

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

    print("\n" + "=" * 70)
    print("STARTING OPPORTUNITY SEARCH")
    print("=" * 70)

    # -----------------------------------------------------
    # BUILD QUERIES
    # -----------------------------------------------------

    queries = _queries(
        profile,
        opportunity_type,
        location,
        work_mode,
        funding,
        custom_keywords,
    )

    print("\nQUERIES:")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    # -----------------------------------------------------
    # DDGS SEARCH
    # -----------------------------------------------------

    raw = []
    seen = set()

    for query in queries:

        results = search_web(
            query,
            max_results=8
        )

        for result in results:

            url = (
                result.get("href")
                or result.get("url")
                or ""
            ).strip()

            title = str(
                result.get("title", "")
            ).strip()

            if not url or not title:
                continue

            key = url.split("#")[0].rstrip("/")

            if key in seen:
                continue

            seen.add(key)

            raw.append({
                "title": title,
                "url": url,
                "summary": str(
                    result.get("body", "")
                    or result.get("snippet", "")
                ),
                "domain": _domain(url),
            })

        # Small delay to reduce DDGS rate-limit problems
        time.sleep(0.5)

    print("\nTOTAL RAW RESULTS:", len(raw))

    # -----------------------------------------------------
    # NO SEARCH RESULTS
    # -----------------------------------------------------

    if not raw:

        print("NO RAW SEARCH RESULTS FOUND.")

        return []

    # -----------------------------------------------------
    # LIMIT AI INPUT
    # -----------------------------------------------------

    raw = raw[:max_results * 2]

    # -----------------------------------------------------
    # CREATE AI PROMPT
    # -----------------------------------------------------

    profile_text = str(profile)

    candidates = "\n\n".join(
        f"""
ID: {i}
TITLE: {x['title']}
URL: {x['url']}
DOMAIN: {x['domain']}
SNIPPET: {x['summary']}
"""
        for i, x in enumerate(raw)
    )

    system = """
You are a career opportunity analyst.

Analyze the supplied web-search results against the candidate profile.

IMPORTANT:
- Do not invent facts.
- Use only information visible in the search candidates.
- A match score is only a fit estimate.
- Do not guarantee employment, admission, scholarship, or funding.
- Keep the original candidate ID.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not include explanations outside the JSON.

Return exactly this structure:

{
  "results": [
    {
      "id": 0,
      "organization": "University or employer",
      "location": "Location or Not stated",
      "type": "Job",
      "funding": "Funding information or Not stated",
      "deadline": "Deadline or Not stated",
      "summary": "Short factual summary",
      "match_score": 75,
      "match_reasons": [
        "Reason 1",
        "Reason 2"
      ]
    }
  ]
}

Allowed type values:
Job
PhD
Scholarship
Research
"""

    user = f"""
Candidate profile:

{profile_text}

Requested opportunity type:
{opportunity_type}

Location:
{location}

Work mode:
{work_mode}

Funding:
{funding}

Search candidates:

{candidates}
"""

    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    try:

        print("\nSending results to Groq for analysis...")

        analysis = ai.json(
            system,
            user
        )

        print("AI RESPONSE TYPE:", type(analysis))

        if not isinstance(analysis, dict):

            print("AI RESPONSE WAS NOT A DICTIONARY.")

            return _make_fallback_results(
                raw,
                max_results
            )

        analyzed_results = analysis.get(
            "results",
            []
        )

        print(
            "AI ANALYZED RESULTS:",
            len(analyzed_results)
        )

    except Exception as e:

        print("\nAI ANALYSIS ERROR:")
        print(type(e).__name__, ":", str(e))

        # IMPORTANT:
        # Do NOT return [].
        # Show raw search results instead.

        return _make_fallback_results(
            raw,
            max_results
        )

    # -----------------------------------------------------
    # CONVERT AI RESULTS
    # -----------------------------------------------------

    output = []

    for a in analyzed_results:

        try:

            idx = int(a.get("id"))

            if idx < 0 or idx >= len(raw):
                continue

            source = raw[idx]

        except Exception:

            continue

        try:

            score = int(
                a.get(
                    "match_score",
                    0
                )
            )

        except Exception:

            score = 0

        score = max(
            0,
            min(100, score)
        )

        reasons = a.get(
            "match_reasons",
            []
        )

        if not isinstance(reasons, list):
            reasons = [str(reasons)]

        item = {
            "title": source["title"],
            "url": source["url"],
            "domain": source["domain"],
            "organization": a.get(
                "organization",
                "Not stated"
            ),
            "location": a.get(
                "location",
                "Not stated"
            ),
            "type": a.get(
                "type",
                "Opportunity"
            ),
            "funding": a.get(
                "funding",
                "Not stated"
            ),
            "deadline": a.get(
                "deadline",
                "Not stated"
            ),
            "summary": a.get(
                "summary",
                source["summary"]
            ),
            "match_score": score,
            "match_reasons": reasons,
        }

        if not _blocked(
            item,
            location,
            exclude_municipal
        ):
            output.append(item)

    # -----------------------------------------------------
    # AI RETURNED NOTHING
    # -----------------------------------------------------

    if not output:

        print(
            "AI returned no usable opportunities."
        )

        print(
            "Using raw search results as fallback."
        )

        return _make_fallback_results(
            raw,
            max_results
        )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    output.sort(
        key=lambda x: x.get(
            "match_score",
            0
        ),
        reverse=True
    )

    final_output = output[:max_results]

    print(
        "\nFINAL OPPORTUNITIES:",
        len(final_output)
    )

    print("=" * 70)

    return final_output
```

### What changed

The biggest change is this:

**Old code:**

```python
except Exception:
    analysis = {"results": []}
```

That was hiding the actual error.

**New code:**

```python
except Exception as e:
    print("\nAI ANALYSIS ERROR:")
    print(type(e).__name__, ":", str(e))

    return _make_fallback_results(raw, max_results)
```

So even if Groq has a temporary JSON/problem, your application **will still show the jobs found by DDGS**.

Also, your previous query:

```text
(civil engineering OR urban planning OR GIS OR smart cities OR geotechnical engineering) jobs ...
```

can behave poorly with search engines. The new version searches separately:

```text
"civil engineering" jobs
"urban planning" jobs
"GIS" jobs
"smart cities" jobs
"geotechnical engineering" jobs
```

which is much more consistent with the DDGS tests that already worked for you.

### Do this now

In GitHub:

**`modules/job_search.py` → Select all → Delete → paste the code above → Commit changes.**

Then wait for Streamlit Cloud to redeploy.

After deployment, click:

**🚀 Search opportunities**

If it still gives no results, the next thing we need is
