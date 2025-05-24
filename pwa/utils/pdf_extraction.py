import logging
import os
from pdfminer.high_level import extract_text

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using PDFMiner.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        Exception: If there's an error during extraction
    """
    try:
        logger.debug(f"Extracting text from PDF: {pdf_path}")
        
        # Check if file exists
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")
        
        # Extract text using PDFMiner
        text = extract_text(pdf_path)
        
        if not text.strip():
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return "No text could be extracted from this PDF. The file might be scanned or contain only images."
        
        logger.debug(f"Successfully extracted {len(text)} characters from PDF")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
