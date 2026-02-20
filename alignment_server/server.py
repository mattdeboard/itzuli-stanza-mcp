"""FastAPI HTTP server for alignment data generation."""

import logging
import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.types import AnalysisRow, LanguageCode
from tools.dual_analysis import analyze_both_texts
from alignment_server.scaffold import create_scaffold_from_dual_analysis
from alignment_server.types import AlignmentData

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Alignment Server",
    description="HTTP API for generating alignment scaffolds from dual language analysis",
    version="0.1.0"
)


class AnalysisRequest(BaseModel):
    """Request model for dual analysis."""
    text: str
    source_lang: LanguageCode
    target_lang: LanguageCode
    sentence_id: str = "default"


class AnalysisResponse(BaseModel):
    """Response model for dual analysis."""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    source_analysis: List[AnalysisRow]
    target_analysis: List[AnalysisRow]


class ScaffoldRequest(BaseModel):
    """Request model for scaffold generation."""
    source_analysis: List[Dict[str, str]]
    target_analysis: List[Dict[str, str]]
    source_text: str
    target_text: str
    source_lang: LanguageCode
    target_lang: LanguageCode
    sentence_id: str = "default"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_texts(request: AnalysisRequest):
    """
    Perform dual analysis on source text and its translation.
    
    Returns analysis data for both source and target languages.
    """
    api_key = os.environ.get("ITZULI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ITZULI_API_KEY not configured")
    
    try:
        source_analysis, target_analysis, translated_text = analyze_both_texts(
            api_key=api_key,
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        return AnalysisResponse(
            source_text=request.text,
            target_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            source_analysis=source_analysis,
            target_analysis=target_analysis
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/scaffold", response_model=AlignmentData)
async def generate_scaffold(request: ScaffoldRequest):
    """
    Generate alignment scaffold from dual analysis data.
    
    Takes analysis results and produces alignment scaffold for annotation.
    """
    try:
        # Convert dictionaries back to AnalysisRow objects
        source_rows = [
            AnalysisRow(
                word=item["word"],
                lemma=item["lemma"],
                upos=item["upos"],
                feats=item["feats"]
            )
            for item in request.source_analysis
        ]
        
        target_rows = [
            AnalysisRow(
                word=item["word"],
                lemma=item["lemma"],
                upos=item["upos"],
                feats=item["feats"]
            )
            for item in request.target_analysis
        ]
        
        alignment_data = create_scaffold_from_dual_analysis(
            source_analysis=source_rows,
            target_analysis=target_rows,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            source_text=request.source_text,
            target_text=request.target_text,
            sentence_id=request.sentence_id
        )
        
        return alignment_data
        
    except Exception as e:
        logger.error(f"Scaffold generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scaffold generation failed: {str(e)}")


@app.post("/analyze-and-scaffold", response_model=AlignmentData)
async def analyze_and_scaffold(request: AnalysisRequest):
    """
    Combined endpoint: analyze both texts and generate scaffold in one call.
    """
    api_key = os.environ.get("ITZULI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ITZULI_API_KEY not configured")
    
    try:
        # First perform dual analysis
        source_analysis, target_analysis, translated_text = analyze_both_texts(
            api_key=api_key,
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        # Then generate scaffold
        alignment_data = create_scaffold_from_dual_analysis(
            source_analysis=source_analysis,
            target_analysis=target_analysis,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            source_text=request.text,
            target_text=translated_text,
            sentence_id=request.sentence_id
        )
        
        return alignment_data
        
    except Exception as e:
        logger.error(f"Analysis and scaffold generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis and scaffold generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting alignment server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)