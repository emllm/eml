from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .core import PEMLParser, PEMLError
from .validator import PEMLValidator
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PEML API",
    description="Python Email Message Language API",
    version="0.1.0"
)

class EmailMessage(BaseModel):
    headers: Dict[str, str] = Field(..., description="Email headers")
    body: str = Field(..., description="Email body content")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="List of attachments")

class PEMLRequest(BaseModel):
    content: str = Field(..., description="PEML content")
    validate: bool = Field(default=False, description="Validate message structure")

class PEMLResponse(BaseModel):
    message: str = Field(..., description="Processed message")
    error: Optional[str] = None
    validation_errors: Optional[List[str]] = None

@app.post("/parse", response_model=PEMLResponse)
async def parse_peml(request: PEMLRequest):
    """Parse PEML content into structured format"""
    try:
        parser = PEMLParser()
        message = parser.parse(request.content)
        result = parser.to_dict(message)
        return PEMLResponse(message=json.dumps(result, indent=2))
    except PEMLError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate", response_model=PEMLResponse)
async def generate_peml(request: PEMLRequest):
    """Generate PEML from structured format"""
    try:
        parser = PEMLParser()
        validator = PEMLValidator()
        
        # Validate if requested
        if request.validate:
            validator.validate(request.message)
        
        # Generate email message
        email_message = parser.from_dict(request.message)
        return PEMLResponse(message=email_message.as_string())
    except (PEMLError, ValueError) as e:
        logger.error(f"Error generating message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate", response_model=PEMLResponse)
async def validate_peml(request: PEMLRequest):
    """Validate PEML content structure"""
    try:
        parser = PEMLParser()
        validator = PEMLValidator()
        
        message = parser.parse(request.content)
        validator.validate(parser.to_dict(message))
        return PEMLResponse(message="Message is valid!")
    except (PEMLError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert")
async def convert_format(
    from_format: str,
    to_format: str,
    content: str = Body(...)
):
    """Convert between formats"""
    if from_format not in ['peml', 'json'] or to_format not in ['peml', 'json']:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    parser = PEMLParser()
    
    if from_format == 'peml':
        message = parser.parse(content)
        result = parser.to_dict(message)
    else:  # json to peml
        message = parser.from_dict(json.loads(content))
        result = message.as_string()
    
    return {"result": result}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}
