import os
import json
from groq import Groq

class AIClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        try:
            import streamlit as st
            if not api_key:
                api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to Streamlit Secrets or environment variables."
            )

        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content.strip()

    def json(self, system: str, user: str):
        raw = self.chat(
            system + "\nReturn ONLY valid JSON. No markdown fences.",
            user,
            temperature=0.1,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start:end + 1])
            raise
