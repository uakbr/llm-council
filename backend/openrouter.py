"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional

from .settings import get_openrouter_credentials


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    client: Optional[httpx.AsyncClient] = None
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenRouter API.

    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    creds = get_openrouter_credentials()
    headers = {
        "Authorization": f"Bearer {creds.api_key}" if creds.api_key else "",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async def _do_request(client_obj: httpx.AsyncClient):
            response = await client_obj.post(
                creds.api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

        if client is not None:
            return await _do_request(client)

        async with httpx.AsyncClient(timeout=timeout) as client_obj:
            return await _do_request(client_obj)

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [query_model(model, messages, timeout=timeout, client=client) for model in models]
        responses = await asyncio.gather(*tasks)

    return {model: response for model, response in zip(models, responses)}
