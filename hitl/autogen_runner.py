import asyncio
from agent import run_agent_async

def run_agent_sync(prompt: str, history: list) -> str:
    """
    Streamlit-safe sync wrapper.
    Creates a fresh event loop per call.
    """
    return run_agent_async(prompt, history)



__all__ = ["run_agent_sync"]
