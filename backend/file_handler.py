"""
File Handler for NEXUS
Processes various file types and extracts content
"""

import io
from typing import Dict, Optional
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image


class FileHandler:
    """Handle file uploads and content extraction"""
    
    SUPPORTED_TEXT = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.xml', '.html', '.css'}
    SUPPORTED_DOCS = {'.pdf', '.docx'}
    SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    @staticmethod
    async def process_file(filename: str, content: bytes) -> Dict:
        """Process uploaded file and extract content"""
        suffix = Path(filename).suffix.lower()
        
        try:
            if suffix in FileHandler.SUPPORTED_TEXT:
                return await FileHandler._process_text(filename, content)
            elif suffix == '.pdf':
                return await FileHandler._process_pdf(filename, content)
            elif suffix == '.docx':
                return await FileHandler._process_docx(filename, content)
            elif suffix in FileHandler.SUPPORTED_IMAGES:
                return await FileHandler._process_image(filename, content)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {suffix}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    @staticmethod
    async def _process_text(filename: str, content: bytes) -> Dict:
        """Process text files"""
        try:
            text = content.decode('utf-8')
            return {
                'success': True,
                'filename': filename,
                'type': 'text',
                'content': text,
                'size': len(content),
                'preview': text[:500] + ('...' if len(text) > 500 else '')
            }
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    text = content.decode(encoding)
                    return {
                        'success': True,
                        'filename': filename,
                        'type': 'text',
                        'content': text,
                        'size': len(content),
                        'preview': text[:500] + ('...' if len(text) > 500 else '')
                    }
                except:
                    continue
            raise
    
    @staticmethod
    async def _process_pdf(filename: str, content: bytes) -> Dict:
        """Process PDF files"""
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())
        
        full_text = '\n\n'.join(text_parts)
        
        return {
            'success': True,
            'filename': filename,
            'type': 'pdf',
            'content': full_text,
            'pages': len(reader.pages),
            'size': len(content),
            'preview': full_text[:500] + ('...' if len(full_text) > 500 else '')
        }
    
    @staticmethod
    async def _process_docx(filename: str, content: bytes) -> Dict:
        """Process DOCX files"""
        doc_file = io.BytesIO(content)
        doc = Document(doc_file)
        
        # Extract text from paragraphs
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = '\n\n'.join(text_parts)
        
        return {
            'success': True,
            'filename': filename,
            'type': 'docx',
            'content': full_text,
            'paragraphs': len(text_parts),
            'size': len(content),
            'preview': full_text[:500] + ('...' if len(full_text) > 500 else '')
        }
    
    @staticmethod
    async def _process_image(filename: str, content: bytes) -> Dict:
        """Process image files"""
        image_file = io.BytesIO(content)
        image = Image.open(image_file)
        
        return {
            'success': True,
            'filename': filename,
            'type': 'image',
            'content': f'Image: {filename}',
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'size': len(content),
            'preview': f'{filename} ({image.width}x{image.height}, {image.format})'
        }
    
    @staticmethod
    def is_supported(filename: str) -> bool:
        """Check if file type is supported"""
        suffix = Path(filename).suffix.lower()
        return suffix in (
            FileHandler.SUPPORTED_TEXT |
            FileHandler.SUPPORTED_DOCS |
            FileHandler.SUPPORTED_IMAGES
        )
