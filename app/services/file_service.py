import os
import aiofiles
import logging
import uuid
from fastapi import UploadFile
from typing import Tuple, Optional
import docling  # For PDF processing

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    async def save_file(file: UploadFile, directory: str) -> Tuple[bool, Optional[str]]:
        """Save an uploaded file to the specified directory."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)

            # Generate unique filename
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(directory, unique_filename)

            # Save the file
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

            logger.info(f"File saved successfully to {file_path}")
            return True, file_path
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return False, None

    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> Tuple[bool, Optional[str]]:
        """Extract text from a PDF file."""
        try:
            # Using docling to extract text (placeholder)
            # In a real implementation, you would use a library like PyPDF2 or docling
            text = "This is extracted text from the PDF."  # Placeholder

            logger.info(f"Text extracted successfully from {file_path}")
            return True, text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return False, None
