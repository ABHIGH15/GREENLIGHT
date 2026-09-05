import asyncio
import time
import re
import os
import logging
from typing import Optional, AsyncGenerator

logger = logging.getLogger("greenlight.rate_limiter")

class DailyQuotaExhaustedError(Exception):
    """Raised when a specific model has exhausted its daily free-tier quota (RPD)."""
    def __init__(self, model: str, message: str):
        super().__init__(f"Daily quota exhausted for model '{model}': {message}")
        self.model = model
        self.raw_message = message

_patched = False
_request_lock = asyncio.Lock()
_last_request_time = 0.0

def setup_adk_rate_limiter(default_min_interval: float = 12.5, default_max_retries: int = 5):
    """Monkey-patches google.adk.models.google_llm.Gemini to add proactive pacing,
    429/503 backoff retries, and quota exhaustion detection.
    """
    global _patched
    if _patched:
        return

    try:
        from google.adk.models.google_llm import Gemini
    except ImportError:
        logger.warning("Could not import Google ADK Gemini class; skipping rate limiter patch.")
        return

    orig_generate_content_async = Gemini.generate_content_async

    # Configurable via environment
    pacing_env = os.environ.get("GEMINI_REQUEST_PACING", "").strip()
    min_interval = float(pacing_env) if pacing_env else default_min_interval
    max_retries = int(os.environ.get("GEMINI_MAX_RETRIES", default_max_retries))

    async def paced_generate_content_async(self, llm_request, stream: bool = False):
        global _last_request_time
        model_name = getattr(llm_request, "model", "unknown")

        for attempt in range(1, max_retries + 1):
            # Proactive request pacing (keeps requests strictly under RPM quota)
            async with _request_lock:
                now = time.time()
                elapsed = now - _last_request_time
                if elapsed < min_interval:
                    wait_time = min_interval - elapsed
                    logger.info(f"⏳ [Rate Limiter] Pacing request for model '{model_name}': waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                _last_request_time = time.time()

            try:
                logger.info(f"🚀 [Gemini] Dispatching request to '{model_name}' (attempt {attempt}/{max_retries})...")
                async for item in orig_generate_content_async(self, llm_request, stream=stream):
                    yield item
                return
            except Exception as e:
                err_str = str(e)
                logger.warning(f"⚠️ [Gemini] Model '{model_name}' returned error on attempt {attempt}: {err_str[:120]}")

                # Check if this is a DAILY quota exhaustion (non-retryable within seconds)
                if "PerDay" in err_str or "GenerateRequestsPerDay" in err_str:
                    logger.error(f"❌ [Rate Limiter] Daily quota exhausted for model '{model_name}'.")
                    raise DailyQuotaExhaustedError(model=model_name, message=err_str) from e

                is_connection_error = (
                    "nodename nor servname" in err_str or
                    "ClientConnectorDNSError" in err_str or
                    "Cannot connect to host" in err_str or
                    "ConnectError" in err_str
                )

                is_retryable = (
                    "429" in err_str or 
                    "RESOURCE_EXHAUSTED" in err_str or 
                    "503" in err_str or 
                    "UNAVAILABLE" in err_str or
                    "high demand" in err_str or
                    is_connection_error
                )

                if is_retryable and attempt < max_retries:
                    if is_connection_error:
                        retry_wait = 3.0 * attempt
                        logger.warning(f"⏳ [Rate Limiter] Connection/DNS retry on attempt {attempt}. Waiting {retry_wait:.1f}s before retry...")
                    elif "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str:
                        retry_wait = 5.0 * attempt
                        logger.warning(f"⏳ [Rate Limiter] 503 Server High Demand on attempt {attempt}. Waiting {retry_wait:.1f}s before retry...")
                    else:
                        match = re.search(r'retry in (\d+(\.\d+)?)s', err_str, re.IGNORECASE)
                        if match:
                            retry_wait = float(match.group(1)) + 2.0
                        else:
                            match_delay = re.search(r"'retryDelay':\s*'(\d+)s'", err_str)
                            if match_delay:
                                retry_wait = float(match_delay.group(1)) + 2.0
                            else:
                                retry_wait = 20.0
                        logger.warning(f"⏳ [Rate Limiter] 429 Resource Exhausted on attempt {attempt}. Sleeping {retry_wait:.1f}s before retry...")
                    
                    await asyncio.sleep(retry_wait)
                    async with _request_lock:
                        _last_request_time = time.time()
                else:
                    logger.error(f"❌ [Gemini] Non-retryable error or exceeded max retries: {e}")
                    raise e

    Gemini.generate_content_async = paced_generate_content_async
    _patched = True
    logger.info(f"✅ ADK Gemini rate limiter successfully initialized (min_interval={min_interval}s, max_retries={max_retries}).")
