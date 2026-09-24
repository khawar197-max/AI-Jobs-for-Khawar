````python
import os
import json
from groq import Groq


class AIClient:

    def __init__(self):

        # -------------------------------------------------
        # Get Groq API key
        # -------------------------------------------------

        api_key = os.getenv("GROQ_API_KEY")

        try:
            import streamlit as st

            if not api_key:
                api_key = st.secrets.get("GROQ_API_KEY")

        except Exception:
            pass

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. "
                "Add it to Streamlit Secrets."
            )

        # -------------------------------------------------
        # Groq client
        # -------------------------------------------------

        self.client = Groq(
            api_key=api_key
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Use the model that we already tested successfully
        # -------------------------------------------------

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

        print(
            "GROQ MODEL:",
            self.model
        )

    # -----------------------------------------------------
    # NORMAL CHAT
    # -----------------------------------------------------

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.2
    ) -> str:

        response = self.client.chat.completions.create(

            model=self.model,

            temperature=temperature,

            messages=[
                {
                    "role": "system",
                    "content": system
                },
                {
                    "role": "user",
                    "content": user
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return content.strip()

    # -----------------------------------------------------
    # JSON RESPONSE
    # -----------------------------------------------------

    def json(
        self,
        system: str,
        user: str
    ):

        json_system = system + """

IMPORTANT:
Return ONLY one valid JSON object.
Do not use Markdown.
Do not use ```json.
Do not write anything before or after the JSON.
"""

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                temperature=0.1,

                messages=[
                    {
                        "role": "system",
                        "content": json_system
                    },
                    {
                        "role": "user",
                        "content": user
                    },
                ],

                # Ask Groq for JSON output
                response_format={
                    "type": "json_object"
                },
            )

            raw = response.choices[0].message.content

            if not raw:
                raise RuntimeError(
                    "Groq returned an empty JSON response."
                )

            raw = raw.strip()

            print(
                "GROQ JSON RESPONSE:",
                raw[:1000]
            )

            return json.loads(raw)

        except Exception as e:

            print(
                "GROQ JSON ERROR:",
                type(e).__name__,
                ":",
                str(e)
            )

            # -------------------------------------------------
            # FALLBACK:
            # Try normal chat without response_format
            # -------------------------------------------------

            try:

                raw = self.chat(
                    json_system,
                    user,
                    temperature=0.1
                )

                raw = raw.strip()

                # Remove Markdown fences if model adds them
                raw = raw.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                ).strip()

                # Find JSON object
                start = raw.find("{")
                end = raw.rfind("}")

                if start >= 0 and end > start:

                    json_text = raw[
                        start:end + 1
                    ]

                    return json.loads(
                        json_text
                    )

                raise ValueError(
                    "No JSON object found in Groq response."
                )

            except Exception as fallback_error:

                print(
                    "GROQ JSON FALLBACK ERROR:",
                    type(fallback_error).__name__,
                    ":",
                    str(fallback_error)
                )

                raise
````

### There is one more thing to check

Go to your **Streamlit Secrets**.

If you have something like:

```text
GROQ_API_KEY = "your-key"
GROQ_MODEL = "some-old-model"
```

then the environment variable will override our default.

For now, either **delete `GROQ_MODEL`** from Secrets, or set it to:

```text
GROQ_MODEL = "openai/gpt-oss-120b"
```

Keep your existing `GROQ_API_KEY`.

### Your complete flow will now be

```text
Streamlit app
      ↓
app.py
      ↓
search_opportunities()
      ↓
DDGS
      ↓
RAW SEARCH RESULTS
      ↓
AIClient
      ↓
openai/gpt-oss-120b
      ↓
JSON analysis
      ↓
opportunities displayed
```

And importantly, if Groq fails, the revised `job_search.py` I gave you earlier **falls back to the raw DDGS results**, rather than silently returning zero.

### Do these two changes only

1. Replace **`modules/ai.py`** with the code above.
2. Check Streamlit Secrets and make sure `GROQ_MODEL` is either absent or:
   `openai/gpt-oss-120b`

Then commit/push and let Streamlit redeploy.

**If it still says no results after this, don't change anything else. Send me the Streamlit deployment error/log output.** At that point we can identify the exact failing line rather than continuing to guess.
