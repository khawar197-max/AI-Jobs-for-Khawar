````python
import os
import json
from groq import Groq


class AIClient:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass

        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing.")

        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"

    def chat(self, system, user, temperature=0.2):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        return response.choices[0].message.content.strip()

    def json(self, system, user):
        raw = self.chat(
            system + "\nReturn ONLY valid JSON.",
            user,
            temperature=0.1,
        )

        raw = raw.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

        try:
            return json.loads(raw)
        except Exception:
            start = raw.find("{")
            end = raw.rfind("}")

            if start != -1 and end != -1:
                return json.loads(raw[start:end + 1])

            raise
````
