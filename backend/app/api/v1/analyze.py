"""
Analysis API endpoints
Document and image analysis using OCR + VLM
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
from backend.app.services.ocr_service import OCRService, OCREngine
from backend.app.services.vlm_service import VLMService, VLMProvider
from backend.app.core.security import get_current_user
from backend.app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/document", response_model=Dict[str, Any])
async def analyze_document(
    file: UploadFile = File(...),
    use_vlm: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze uploaded document using OCR and optionally VLM

    Args:
        file: Uploaded document (PDF, image)
        use_vlm: Whether to use VLM for enhanced analysis
        current_user: Current authenticated user

    Returns:
        Document analysis results
    """
    try:
        # Read file data
        file_data = await file.read()

        # Initialize OCR service
        ocr_service = OCRService(engine=OCREngine.PADDLEOCR)

        # Extract text using OCR
        ocr_result = await ocr_service.process_document(file_data)

        response = {
            "text": ocr_result.text,
            "confidence": ocr_result.confidence,
            "entities": ocr_result.entities,
            "document_type": ocr_result.metadata.get("document_type", "unknown"),
            "page_count": ocr_result.metadata.get("pages", 1)
        }

        # Optionally use VLM for enhanced analysis
        if use_vlm:
            try:
                vlm_service = VLMService(provider=VLMProvider.GPT4V)

                # Determine analysis type based on document classification
                doc_type = ocr_result.metadata.get("document_type", "")

                if "financial" in doc_type.lower():
                    vlm_result = await vlm_service.analyze_financial_document(file_data)
                elif "chart" in doc_type.lower() or "graph" in doc_type.lower():
                    vlm_result = await vlm_service.analyze_chart(file_data)
                else:
                    vlm_result = await vlm_service.analyze_image(
                        file_data,
                        "Analyze this document and provide key insights."
                    )

                response["vlm_analysis"] = vlm_result.get("analysis", "")
                response["vlm_provider"] = vlm_result.get("provider", "")

            except Exception as e:
                logger.warning(f"VLM analysis failed: {e}")
                response["vlm_analysis"] = None
                response["vlm_error"] = str(e)

        return response

    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@router.post("/image", response_model=Dict[str, Any])
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = "Analyze this image and provide insights.",
    current_user: User = Depends(get_current_user)
):
    """
    Analyze uploaded image using VLM

    Args:
        file: Uploaded image
        prompt: Analysis prompt
        current_user: Current authenticated user

    Returns:
        Image analysis results
    """
    try:
        file_data = await file.read()

        # Initialize VLM service
        vlm_service = VLMService(provider=VLMProvider.GPT4V)

        # Validate image
        if not vlm_service.validate_image(file_data):
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Analyze image
        result = await vlm_service.analyze_image(file_data, prompt)

        return {
            "analysis": result.get("analysis", ""),
            "model": result.get("model", ""),
            "provider": result.get("provider", ""),
            "prompt": prompt
        }

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@router.post("/chart", response_model=Dict[str, Any])
async def analyze_chart(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze chart or graph using VLM

    Args:
        file: Uploaded chart image
        current_user: Current authenticated user

    Returns:
        Chart analysis with trends and insights
    """
    try:
        file_data = await file.read()

        vlm_service = VLMService(provider=VLMProvider.GPT4V)
        result = await vlm_service.analyze_chart(file_data)

        return result

    except Exception as e:
        logger.error(f"Chart analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chart analysis failed: {str(e)}")


@router.post("/financial-document", response_model=Dict[str, Any])
async def analyze_financial_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze financial document using OCR + VLM

    Args:
        file: Uploaded financial document
        current_user: Current authenticated user

    Returns:
        Financial document analysis
    """
    try:
        file_data = await file.read()

        # Use both OCR and VLM
        ocr_service = OCRService(engine=OCREngine.AWS_TEXTRACT)
        ocr_result = await ocr_service.extract_forms(file_data)

        vlm_service = VLMService(provider=VLMProvider.GPT4V)
        vlm_result = await vlm_service.analyze_financial_document(file_data)

        return {
            "text_extraction": {
                "text": ocr_result.text,
                "entities": ocr_result.entities,
                "forms": ocr_result.metadata.get("forms", {})
            },
            "visual_analysis": vlm_result.get("analysis", ""),
            "combined_insights": f"{ocr_result.text}\n\nVLM Insights:\n{vlm_result.get('analysis', '')}"
        }

    except Exception as e:
        logger.error(f"Financial document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
