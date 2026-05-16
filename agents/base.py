"""
Base agent class for all Inshira Growth OS agents.
"""
import json
from typing import Any, Dict, List, Optional
import anthropic
from config import ANTHROPIC_API_KEY, MODEL_COMPLEX, MODEL_VOLUME
from memory.crm import CRM


class BaseAgent:
    """
    Every agent inherits from BaseAgent.
    - Holds a reference to the shared CRM
    - Calls the Anthropic API with a structured system prompt
    - Returns parsed JSON output
    """

    name: str = "BaseAgent"
    model: str = MODEL_COMPLEX
    system_prompt: str = "You are an AI agent."

    def __init__(self, crm: CRM):
        self.crm = crm
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def _call(self, user_message: str, max_tokens: int = 4096) -> str:
        """
        Call the Anthropic API and return the text response.
        Adds a JSON instruction to the system prompt so outputs are parseable.
        """
        system = (
            self.system_prompt
            + "\n\nAlways respond with valid JSON. "
              "Do not include markdown code fences. "
              "Do not include any text outside the JSON object."
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()

    def _call_json(self, user_message: str, max_tokens: int = 4096) -> Dict:
        """Call the API and parse the JSON response."""
        raw = self._call(user_message, max_tokens)
        # Strip markdown fences if present despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: return raw text in a wrapper
            return {"raw_output": raw, "parse_error": True}

    def run(self, context: Dict) -> Dict:
        """Override in each agent subclass."""
        raise NotImplementedError
