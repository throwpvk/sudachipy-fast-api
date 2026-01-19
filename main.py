from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sudachipy import tokenizer
from sudachipy import dictionary
import uvicorn

app = FastAPI(
    title="SudachiPy API",
    description="API for Japanese text tokenization and normalization using SudachiPy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SudachiPy tokenizer with full dictionary
tokenizer_obj = dictionary.Dictionary(dict="full").create()
mode = tokenizer.Tokenizer.SplitMode.C  # C mode for best granularity


class Token(BaseModel):
    surface: str
    base: str
    pos: str
    reading: Optional[str] = None


class Sentence(BaseModel):
    id: int
    raw: str


class ProcessRequest(BaseModel):
    sentences: List[Sentence]


class ProcessedSentence(BaseModel):
    id: int
    raw: str
    normalized: str
    normalized_spaced: str
    tokens: List[Token]


class ProcessResponse(BaseModel):
    success: bool
    sentences: List[ProcessedSentence]


class TokenizeRequest(BaseModel):
    text: str


class TokenizeResponse(BaseModel):
    success: bool
    raw: str
    normalized: str
    normalized_spaced: str
    tokens: List[Token]


def process_text(text: str) -> dict:
    """Process Japanese text with SudachiPy"""
    try:
        # Tokenize
        morphemes = tokenizer_obj.tokenize(text, mode)
        
        tokens = []
        normalized_parts = []
        
        for m in morphemes:
            # Get normalized form (基本形)
            base_form = m.normalized_form()
            surface = m.surface()
            
            # Get part of speech (品詞)
            pos_tags = m.part_of_speech()
            pos = pos_tags[0] if pos_tags else "不明"
            
            # Get reading if available
            reading = m.reading_form() if hasattr(m, 'reading_form') else None
            
            tokens.append({
                "surface": surface,
                "base": base_form,
                "pos": pos,
                "reading": reading
            })
            
            normalized_parts.append(base_form)
        
        # Create normalized text (without spaces)
        normalized = "".join(normalized_parts)
        
        # Create normalized spaced text
        normalized_spaced = " ".join(normalized_parts)
        
        return {
            "normalized": normalized,
            "normalized_spaced": normalized_spaced,
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "SudachiPy API",
        "status": "running",
        "endpoints": {
            "/health": "Health check",
            "/tokenize": "Tokenize single text",
            "/process": "Process multiple sentences"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sudachipy-api",
        "version": "1.0.0"
    }


@app.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(request: TokenizeRequest):
    """
    Tokenize and normalize a single Japanese text
    """
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    result = process_text(request.text)
    
    return {
        "success": True,
        "raw": request.text,
        **result
    }


@app.post("/process", response_model=ProcessResponse)
async def process_sentences(request: ProcessRequest):
    """
    Process multiple sentences with tokenization and normalization
    This is the main endpoint for the NestJS backend to call
    """
    if not request.sentences or len(request.sentences) == 0:
        raise HTTPException(status_code=400, detail="Sentences list cannot be empty")
    
    processed_sentences = []
    
    for sentence in request.sentences:
        if not sentence.raw or sentence.raw.strip() == "":
            # Skip empty sentences
            continue
            
        try:
            result = process_text(sentence.raw)
            
            processed_sentences.append({
                "id": sentence.id,
                "raw": sentence.raw,
                **result
            })
        except Exception as e:
            # Log error but continue processing other sentences
            print(f"Error processing sentence {sentence.id}: {str(e)}")
            # Return sentence with empty tokens if processing fails
            processed_sentences.append({
                "id": sentence.id,
                "raw": sentence.raw,
                "normalized": sentence.raw,
                "normalized_spaced": sentence.raw,
                "tokens": []
            })
    
    return {
        "success": True,
        "sentences": processed_sentences
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
