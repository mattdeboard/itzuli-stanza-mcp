"""FastAPI HTTP server for alignment data generation."""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from Itzuli import Itzuli
from pydantic import BaseModel

from ..core.nlp import process_raw_analysis
from ..core.types import LanguageCode
from ..tools.dual_analysis import get_cached_pipeline
from .alignment_generator import create_enriched_alignment_data
from .cache import AlignmentCache
from .rate_limiter import check_and_increment
from .types import AlignmentData
from .types import SentencePair as SentencePairModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Alignment Server",
    description="HTTP API for generating alignment scaffolds from dual language analysis",
    version="1.0.0",
)

# Initialize cache
cache = AlignmentCache()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    """Request model for dual analysis."""

    text: str
    source_lang: LanguageCode
    target_lang: LanguageCode
    sentence_id: str = "default"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.options("/analyze-and-scaffold")
async def options_analyze_and_scaffold():
    """Handle preflight OPTIONS request for analyze-and-scaffold endpoint."""
    return {"message": "OK"}


@app.post("/analyze-and-scaffold")
async def analyze_and_scaffold(request: AnalysisRequest, req: Request):
    """
    Combined endpoint: analyze both texts, generate scaffold, and enrich with Claude-generated alignments.
    Streams SSE events as each stage completes: itzuli_done, stanza_done, done.
    Cache hits are free and bypass rate limiting.
    """
    itzuli_api_key = os.environ.get("ITZULI_API_KEY")
    if not itzuli_api_key:
        raise HTTPException(status_code=500, detail="ITZULI_API_KEY not configured")

    claude_api_key = os.environ.get("CLAUDE_API_KEY")
    if not claude_api_key:
        raise HTTPException(status_code=500, detail="CLAUDE_API_KEY not configured")

    # Cache check first — hits are free, don't count against rate limit
    cached_data = cache.get(request.text, request.source_lang, request.target_lang)
    if cached_data:
        logger.info(f"Cache hit for text: {request.text[:50]}...")
        result = cached_data.sentences[0].model_dump()

        async def _cached_stream():
            yield f"data: {json.dumps({'event': 'done', 'result': result})}\n\n"

        return StreamingResponse(_cached_stream(), media_type="text/event-stream")

    # Rate limit only applies to actual API work
    ip = (req.headers.get("X-Forwarded-For") or req.client.host or "unknown").split(",")[0].strip()
    allowed, remaining = await check_and_increment(ip)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limited", "message": "Daily limit reached. Try again tomorrow."},
        )
    logger.info(f"Rate limit check passed for {ip}: {remaining} requests remaining today")

    async def _stream():
        try:
            # Step 1: Itzuli translation
            itzuli_client = Itzuli(itzuli_api_key)
            translation_data = itzuli_client.getTranslation(
                request.text, request.source_lang, request.target_lang
            )
            translated_text = translation_data.get("translated_text", "")
            logger.info(f"Translation: '{request.text}' -> '{translated_text}'")
            yield f"data: {json.dumps({'event': 'itzuli_done'})}\n\n"

            # Step 2: Stanza analysis
            # Pipelines load from disk on first call (~5 min). Run in a thread and send
            # SSE keepalive comments every 15s so Fly's proxy doesn't close the idle connection.
            pipeline_task = asyncio.create_task(
                asyncio.to_thread(
                    lambda: (get_cached_pipeline(request.source_lang), get_cached_pipeline(request.target_lang))
                )
            )
            while not pipeline_task.done():
                yield ": keepalive\n\n"
                await asyncio.sleep(15)
            source_pipeline, target_pipeline = await pipeline_task
            source_analysis = process_raw_analysis(source_pipeline, request.text)
            target_analysis = process_raw_analysis(target_pipeline, translated_text)
            logger.info(f"Stanza: {len(source_analysis)} source tokens, {len(target_analysis)} target tokens")
            yield f"data: {json.dumps({'event': 'stanza_done'})}\n\n"

            # Step 3: Claude alignment generation
            alignment_data = create_enriched_alignment_data(
                source_analysis=source_analysis,
                target_analysis=target_analysis,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                source_text=request.text,
                target_text=translated_text,
                sentence_id=request.sentence_id,
                claude_api_key=claude_api_key,
            )
            result = alignment_data.sentences[0].model_dump()
            # Strip degenerate alignments Claude occasionally produces (empty source or target)
            for layer in ("lexical", "grammatical_relations", "features"):
                result["layers"][layer] = [
                    a for a in result["layers"][layer] if a["source"] and a["target"]
                ]
            clean_data = AlignmentData(sentences=[SentencePairModel.model_validate(result)])
            cache.set(request.text, request.source_lang, request.target_lang, clean_data)
            yield f"data: {json.dumps({'event': 'done', 'result': result})}\n\n"

        except Exception as e:
            logger.error(f"Analysis and alignment generation failed: {e}")
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting alignment server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
