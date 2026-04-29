"""Mock LLM + embeddings for offline development.

Activated by LLM_MODE=mock in .env. Returns deterministic templated responses
so the chat agent, slide agent, and embedding service all work without Ollama
or any external service.
"""
import hashlib
import re
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockChatLLM(BaseChatModel):
    """Stub chat model. Inspects the last human message and responds heuristically."""

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **_: Any) -> ChatResult:
        text = self._render_response(messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    async def _agenerate(self, messages: list[BaseMessage], stop=None, run_manager=None, **_: Any) -> ChatResult:
        return self._generate(messages, stop=stop, run_manager=run_manager)

    def _render_response(self, messages: list[BaseMessage]) -> str:
        last_human = next((m.content for m in reversed(messages) if m.type == "human"), "")
        system = next((m.content for m in messages if m.type == "system"), "")

        # Slide AI-token resolver path
        if "PowerPoint" in system or "Token:" in last_human:
            return _slide_narrative(last_human)

        # Conversational platform agent path — read the retrieved context out of the system prompt
        return _chat_response(last_human, system)


class MockEmbeddings(Embeddings):
    """Deterministic embeddings — hash the text to fill a 768-dim vector."""

    DIM = 768

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        # Stretch the SHA-256 of the text into 768 floats in [-1, 1]
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        out: list[float] = []
        i = 0
        while len(out) < self.DIM:
            byte = seed[i % len(seed)]
            out.append((byte / 127.5) - 1.0)
            i += 1
        return out


def _chat_response(question: str, system_context: str) -> str:
    q = question.lower()
    ctx_excerpt = _excerpt_context(system_context)

    if "at risk" in q or "risk" in q:
        return (
            "Based on the platform data, FirstNet Expansion is currently flagged as at-risk. "
            "Other programs (5G Core Modernization, Fiber Acceleration) remain on track; "
            "Enterprise AI Platform is in planning. "
            f"{ctx_excerpt}"
        )
    if "program" in q and ("list" in q or "what" in q or "which" in q or "all" in q):
        return (
            "Active programs: 5G Core Modernization (on track), FirstNet Expansion (at risk), "
            "Fiber Acceleration (on track), Enterprise AI Platform (planning). "
            f"{ctx_excerpt}"
        )
    if "adoption" in q or "copilot" in q or "tool" in q:
        return (
            "AI tool adoption is led by GitHub Copilot and Claude Code, both with majority adoption. "
            "Cursor and ChatGPT Enterprise are in active rollout; Databricks Genie is piloting in data teams. "
            f"{ctx_excerpt}"
        )
    if "team" in q or "member" in q or "roster" in q:
        return (
            "Teams span Network (Core, Radio, Ops), Consumer Mobility/Broadband, and Enterprise (Security, Cloud, IoT). "
            f"{ctx_excerpt}"
        )
    if "utiliz" in q or "alloc" in q:
        return (
            "Average resource allocation across teams is approximately 65-80%. "
            "Cloud Solutions and Mobility App teams are most heavily allocated. "
            f"{ctx_excerpt}"
        )

    return (
        "(Mock LLM) I can answer questions about programs, portfolios, teams, resources, and AI adoption. "
        "Try asking which programs are at risk, or what AI tools have been rolled out. "
        f"{ctx_excerpt}"
    )


def _excerpt_context(system_context: str) -> str:
    """Pull a short snippet from retrieved context so responses feel grounded."""
    m = re.search(r"Context retrieved from the platform:\s*(.+)", system_context, re.DOTALL)
    if not m:
        return ""
    body = m.group(1).strip()
    if not body or body.startswith("(no context"):
        return ""
    snippet = body[:240].replace("\n", " ")
    return f"\n\nContext: {snippet}…"


def _slide_narrative(prompt: str) -> str:
    name_match = re.search(r"Token:\s*\{\{([A-Z_]+)\}\}", prompt)
    name = name_match.group(1) if name_match else "SECTION"

    templates = {
        "EXEC_SUMMARY": (
            "This quarter delivered measurable progress across our flagship programs. "
            "5G Core Modernization remains on track, with cloud-native function deployment ahead of plan. "
            "AI tooling adoption continues to climb, with majority engagement on code-assist platforms."
        ),
        "RISKS": (
            "The primary risk is FirstNet Expansion timeline pressure driven by site-acquisition delays. "
            "Mitigation is underway via parallel build crews and updated vendor SLAs. "
            "No other programs are flagged red at this time."
        ),
        "DECISIONS": (
            "Key decisions: approve the GPU capacity increase for the Enterprise AI Platform pilot; "
            "consolidate two overlapping fiber workstreams into a single delivery track; "
            "advance Claude Code from pilot to active for the Cloud Solutions team."
        ),
        "ACTIONS": (
            "Next steps include finalizing the 5G core cutover runbook, completing FirstNet site dependency mapping, "
            "and publishing the AI adoption scorecard to portfolio leads by end of period."
        ),
        "INSIGHTS": (
            "Resource utilization is healthy at 65-80% across most teams. "
            "AI tooling correlates with measurable velocity improvement on code-heavy workstreams. "
            "Portfolio spread for the Enterprise AI Platform indicates cross-organization investment."
        ),
        "NARRATIVE": (
            "Programs progressed on plan with focused execution across portfolios. "
            "Investment in AI capability and platform modernization continues to compound."
        ),
        "NOTES": "Generated by the platform's mock narrative engine for development purposes.",
    }

    for key, text in templates.items():
        if key in name:
            return text
    return f"(Mock narrative for {name}) Section content based on current platform data and trajectory."
