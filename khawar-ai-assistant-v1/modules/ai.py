import os
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

        text = self.chat(
            system,
            user,
            temperature=0.1
        )

        return self._extract_json(text)

    def _extract_json(self, text):

        text = text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end > start:
            text = text[start:end + 1]

        import json

        return json.loads(text)
