from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from emllm.core import emllmParser, emllmError
from emllm.validator import emllmValidator
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="emllm API",
    description="Python Email Message Language API",
    version="0.1.0"
)

class EmailMessage(BaseModel):
    headers: Dict[str, str] = Field(..., description="Email headers")
    body: str = Field(..., description="Email body content")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="List of attachments")

class emllmRequest(BaseModel):
    content: str = Field(..., description="emllm content")
    validate: bool = Field(default=False, description="Validate message structure")

class emllmResponse(BaseModel):
    message: str = Field(..., description="Processed message")
    error: Optional[str] = None
    validation_errors: Optional[List[str]] = None

@app.post("/parse", response_model=emllmResponse)
async def parse_emllm(request: emllmRequest):
    """Parse emllm content into structured format"""
    try:
        parser = emllmParser()
        message = parser.parse(request.content)
        result = parser.to_dict(message)
        return emllmResponse(message=json.dumps(result, indent=2))
    except emllmError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate", response_model=emllmResponse)
async def generate_emllm(request: emllmRequest):
    """Generate emllm from structured format"""
    try:
        parser = emllmParser()
        validator = emllmValidator()
        
        # Validate if requested
        if request.validate:
            validator.validate(request.message)
        
        # Generate email message
        email_message = parser.from_dict(request.message)
        return emllmResponse(message=email_message.as_string())
    except (emllmError, ValueError) as e:
        logger.error(f"Error generating message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate", response_model=emllmResponse)
async def validate_emllm(request: emllmRequest):
    """Validate emllm content structure"""
    try:
        parser = emllmParser()
        validator = emllmValidator()
        
        message = parser.parse(request.content)
        validator.validate(parser.to_dict(message))
        return emllmResponse(message="Message is valid!")
    except (emllmError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert")
async def convert_format(
    from_format: str,
    to_format: str,
    content: str = Body(...)
):
    """Convert between formats"""
    if from_format not in ['emllm', 'json'] or to_format not in ['emllm', 'json']:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    parser = emllmParser()
    
    if from_format == 'emllm':
        message = parser.parse(content)
        result = parser.to_dict(message)
    else:  # json to emllm
        message = parser.from_dict(json.loads(content))
        result = message.as_string()
    
    return {"result": result}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}
