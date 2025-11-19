"""
OCR Service - Document Processing and Text Extraction
Supports multiple OCR engines: Tesseract, PaddleOCR, AWS Textract
"""
from typing import Dict, Any, Optional, List, BinaryIO
from enum import Enum
from dataclasses import dataclass
import io
import base64


class OCREngine(str, Enum):
    """Supported OCR engines"""
    TESSERACT = "tesseract"
    PADDLEOCR = "paddleocr"
    DOCTOCR = "doctrocr"
    AWS_TEXTRACT = "aws_textract"


@dataclass
class OCRResult:
    """OCR extraction result"""
    text: str
    confidence: float
    metadata: Dict[str, Any]
    structured_data: Optional[Dict[str, Any]] = None  # For forms/tables


class TesseractOCR:
    """Tesseract OCR implementation"""

    def __init__(self, lang: str = "eng"):
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            raise ImportError("Please install: pip install pytesseract pillow")

        self.lang = lang
        self.pytesseract = pytesseract
        self.Image = Image

    def extract_text(self, image_data: bytes) -> OCRResult:
        """Extract text from image"""
        image = self.Image.open(io.BytesIO(image_data))

        # Get text with confidence
        data = self.pytesseract.image_to_data(image, lang=self.lang, output_type=self.pytesseract.Output.DICT)

        # Extract full text
        text = self.pytesseract.image_to_string(image, lang=self.lang)

        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            text=text,
            confidence=avg_confidence / 100.0,
            metadata={
                "engine": "tesseract",
                "language": self.lang,
                "image_size": image.size
            }
        )


class PaddleOCR:
    """PaddleOCR implementation (better for complex layouts)"""

    def __init__(self, lang: str = "en"):
        try:
            from paddleocr import PaddleOCR as PaddleOCREngine
        except ImportError:
            raise ImportError("Please install: pip install paddleocr")

        self.lang = lang
        self.ocr = PaddleOCREngine(use_angle_cls=True, lang=lang, show_log=False)

    def extract_text(self, image_data: bytes) -> OCRResult:
        """Extract text from image"""
        import numpy as np
        from PIL import Image

        # Load image
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        # Run OCR
        result = self.ocr.ocr(image_np, cls=True)

        # Extract text and confidence
        all_text = []
        all_confidence = []

        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                all_text.append(text)
                all_confidence.append(confidence)

        full_text = "\n".join(all_text)
        avg_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0.0

        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            metadata={
                "engine": "paddleocr",
                "language": self.lang,
                "lines_detected": len(all_text)
            }
        )


class AWSTextractOCR:
    """AWS Textract for advanced document processing"""

    def __init__(self, aws_access_key: str = None, aws_secret_key: str = None, region: str = "us-east-1"):
        try:
            import boto3
        except ImportError:
            raise ImportError("Please install: pip install boto3")

        self.client = boto3.client(
            'textract',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

    def extract_text(self, image_data: bytes) -> OCRResult:
        """Extract text using AWS Textract"""
        # Detect document text
        response = self.client.detect_document_text(
            Document={'Bytes': image_data}
        )

        # Extract text and confidence
        all_text = []
        all_confidence = []

        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                all_text.append(block['Text'])
                all_confidence.append(block['Confidence'] / 100.0)

        full_text = "\n".join(all_text)
        avg_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0.0

        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            metadata={
                "engine": "aws_textract",
                "blocks_detected": len(response['Blocks'])
            }
        )

    def extract_forms(self, image_data: bytes) -> OCRResult:
        """Extract forms and key-value pairs"""
        response = self.client.analyze_document(
            Document={'Bytes': image_data},
            FeatureTypes=['FORMS']
        )

        # Extract key-value pairs
        key_map = {}
        value_map = {}
        block_map = {}

        for block in response['Blocks']:
            block_id = block['Id']
            block_map[block_id] = block

            if block['BlockType'] == "KEY_VALUE_SET":
                if 'KEY' in block['EntityTypes']:
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block

        # Build structured data
        structured_data = {}
        for key_id, key_block in key_map.items():
            value_block_id = None
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        value_block_id = relationship['Ids'][0]

            key_text = self._get_text(key_block, block_map)
            value_text = self._get_text(block_map.get(value_block_id, {}), block_map) if value_block_id else ""

            structured_data[key_text] = value_text

        # Also get plain text
        all_text = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                all_text.append(block['Text'])

        return OCRResult(
            text="\n".join(all_text),
            confidence=0.95,  # Textract is generally high confidence
            metadata={"engine": "aws_textract", "type": "form_extraction"},
            structured_data=structured_data
        )

    def _get_text(self, block: Dict, block_map: Dict) -> str:
        """Helper to extract text from a block"""
        text = ""
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child = block_map.get(child_id, {})
                        if child.get('BlockType') == 'WORD':
                            text += child.get('Text', '') + ' '
        return text.strip()


class DocumentPreprocessor:
    """Preprocesses documents before OCR"""

    @staticmethod
    def preprocess_image(image_data: bytes) -> bytes:
        """
        Preprocess image for better OCR results

        Steps:
        - Deskewing
        - Denoising
        - Contrast enhancement
        - Binarization
        """
        try:
            import cv2
            import numpy as np
            from PIL import Image
        except ImportError:
            # If OpenCV not available, return original
            return image_data

        # Load image
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        # Convert to grayscale
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # Binarization (Otsu's method)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert back to PIL Image
        result_image = Image.fromarray(binary)

        # Save to bytes
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        return output.getvalue()


class DocumentAnalyzer:
    """Analyze extracted document text"""

    def __init__(self):
        pass

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text

        Returns entities like:
        - Dates
        - Monetary amounts
        - Company names
        - People names
        """
        import re

        entities = {
            "dates": [],
            "amounts": [],
            "emails": [],
            "phones": []
        }

        # Extract dates (simple pattern)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text)

        # Extract monetary amounts
        amount_pattern = r'[$₹€£]\s?\d+(?:,\d{3})*(?:\.\d{2})?'
        entities["amounts"] = re.findall(amount_pattern, text)

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, text)

        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["phones"] = re.findall(phone_pattern, text)

        return entities

    def classify_document_type(self, text: str) -> str:
        """Classify document type based on content"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in ["invoice", "bill", "payment due"]):
            return "invoice"
        elif any(keyword in text_lower for keyword in ["agreement", "contract", "party", "whereas"]):
            return "contract"
        elif any(keyword in text_lower for keyword in ["balance sheet", "income statement", "financial"]):
            return "financial_statement"
        elif any(keyword in text_lower for keyword in ["policy", "regulation", "compliance"]):
            return "policy_document"
        else:
            return "general"


class OCRService:
    """
    Main OCR service that orchestrates document processing
    """

    def __init__(self, engine: OCREngine = OCREngine.PADDLEOCR):
        """
        Initialize OCR service

        Args:
            engine: OCR engine to use
        """
        self.engine = engine
        self.preprocessor = DocumentPreprocessor()
        self.analyzer = DocumentAnalyzer()
        self.ocr_client = self._create_ocr_client()

    def _create_ocr_client(self):
        """Create OCR client based on engine type"""
        if self.engine == OCREngine.TESSERACT:
            return TesseractOCR()
        elif self.engine == OCREngine.PADDLEOCR:
            return PaddleOCR()
        elif self.engine == OCREngine.AWS_TEXTRACT:
            return AWSTextractOCR()
        else:
            return PaddleOCR()  # Default

    async def process_document(
        self,
        file_data: bytes,
        preprocess: bool = True,
        extract_entities: bool = True,
        classify: bool = True
    ) -> Dict[str, Any]:
        """
        Process a document with OCR

        Args:
            file_data: Document file as bytes
            preprocess: Whether to preprocess the image
            extract_entities: Whether to extract entities
            classify: Whether to classify document type

        Returns:
            Processing result with text, entities, and metadata
        """
        # Preprocess if requested
        if preprocess:
            processed_data = self.preprocessor.preprocess_image(file_data)
        else:
            processed_data = file_data

        # Run OCR
        ocr_result = self.ocr_client.extract_text(processed_data)

        # Extract entities if requested
        entities = None
        if extract_entities:
            entities = self.analyzer.extract_entities(ocr_result.text)

        # Classify document if requested
        doc_type = None
        if classify:
            doc_type = self.analyzer.classify_document_type(ocr_result.text)

        return {
            "text": ocr_result.text,
            "confidence": ocr_result.confidence,
            "document_type": doc_type,
            "entities": entities,
            "structured_data": ocr_result.structured_data,
            "metadata": ocr_result.metadata
        }

    async def process_pdf(self, pdf_data: bytes) -> List[Dict[str, Any]]:
        """
        Process a PDF document (multi-page)

        Args:
            pdf_data: PDF file as bytes

        Returns:
            List of results, one per page
        """
        try:
            from pdf2image import convert_from_bytes
        except ImportError:
            raise ImportError("Please install: pip install pdf2image")

        # Convert PDF to images
        images = convert_from_bytes(pdf_data)

        # Process each page
        results = []
        for i, image in enumerate(images):
            # Convert PIL image to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()

            # Process page
            result = await self.process_document(img_bytes)
            result["page_number"] = i + 1

            results.append(result)

        return results


# Factory function
def create_ocr_service(engine: str = "paddleocr") -> OCRService:
    """
    Factory function to create OCR service

    Args:
        engine: OCR engine name

    Returns:
        OCRService instance
    """
    engine_enum = OCREngine(engine)
    return OCRService(engine=engine_enum)
