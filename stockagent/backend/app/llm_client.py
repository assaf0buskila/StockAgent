"""
LLM client for interacting with Ollama.

This module handles all communication with the local LLM service.
"""

import httpx
from typing import Optional
from .config import settings


async def ask_llm(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Send a prompt to the LLM and get a response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name override (uses settings.LLM_MODEL_NAME if None)
        temperature: Sampling temperature (0.0 to 1.0)
            - Lower = more focused and deterministic
            - Higher = more creative and diverse
        max_tokens: Maximum tokens in response (None = model default)
        
    Returns:
        str: The LLM's response text
        
    Raises:
        Exception: If the LLM request fails
    """
    url = f"{settings.LLM_BASE_URL}/api/generate"
    model_name = model or settings.LLM_MODEL_NAME
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,"num_predict": max_tokens or 512,
        }
    }
    
    # Add max_tokens if specified
    if max_tokens:
        payload["options"]["num_predict"] = max_tokens
    
    print(f"[DEBUG] Sending request to LLM: {model_name}")
    print(f"[DEBUG] Prompt length: {len(prompt)} characters")
    print(f"[DEBUG] Temperature: {temperature}")
    
    # Use increased timeout from settings
    timeout = httpx.Timeout(settings.LLM_TIMEOUT, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            response_text = data.get("response", "")
            
            if not response_text:
                raise ValueError("Empty response from LLM")
            
            print(f"[DEBUG] LLM response length: {len(response_text)} characters")
            return response_text
            
        except httpx.ConnectError as exc:
            error_msg = (
                f"Cannot connect to LLM service at {settings.LLM_BASE_URL}. "
                "Please ensure Ollama is running:\n"
                "  1. Install Ollama from https://ollama.ai\n"
                f"  2. Run: ollama pull {model_name}\n"
                "  3. Start Ollama service"
            )
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from exc
            
        except httpx.TimeoutException as exc:
            error_msg = (
                f"LLM request timed out after {settings.LLM_TIMEOUT}s. "
                "The model might be too slow or the prompt too complex. "
                "Try:\n"
                "  1. Using a smaller model\n"
                "  2. Increasing LLM_TIMEOUT in config\n"
                "  3. Simplifying the prompt"
            )
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from exc
            
        except httpx.HTTPStatusError as exc:
            error_msg = (
                f"LLM service returned error {exc.response.status_code}. "
                f"URL: {exc.request.url}\n"
                f"Details: {exc.response.text}"
            )
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from exc
            
        except KeyError as exc:
            error_msg = (
                "Unexpected response format from LLM. "
                f"Missing key: {exc}\n"
                f"Response: {data}"
            )
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from exc
            
        except Exception as exc:
            error_msg = f"Unexpected error during LLM request: {type(exc).__name__}: {exc}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from exc


async def test_llm_connection() -> dict:
    """
    Test the connection to the LLM service.
    
    Returns:
        dict: Status information about the LLM connection
    """
    try:
        response = await ask_llm(
            "Respond with only the word 'connected' if you receive this message.",
            temperature=0.1
        )
        
        return {
            "status": "connected",
            "model": settings.LLM_MODEL_NAME,
            "url": settings.LLM_BASE_URL,
            "response": response[:100]  # First 100 chars
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "model": settings.LLM_MODEL_NAME,
            "url": settings.LLM_BASE_URL,
            "error": str(e)
        }