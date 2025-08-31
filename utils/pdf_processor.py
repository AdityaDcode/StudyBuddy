import pdfplumber
import streamlit as st
from io import BytesIO

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from PDF
        """
        try:
            # Create a BytesIO object from uploaded file
            pdf_bytes = BytesIO(uploaded_file.read())
            
            # Extract text using pdfplumber
            extracted_text = ""
            
            with pdfplumber.open(pdf_bytes) as pdf:
                total_pages = len(pdf.pages)
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, page in enumerate(pdf.pages):
                    # Update progress
                    progress = (i + 1) / total_pages
                    progress_bar.progress(progress)
                    status_text.text(f"Processing page {i + 1} of {total_pages}")
                    
                    # Extract text from current page
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n\n"
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
            
            if not extracted_text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return self._clean_text(extracted_text)
            
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _clean_text(self, text):
        """
        Clean and normalize extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def get_text_stats(self, text):
        """
        Get statistics about the extracted text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Text statistics
        """
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'character_count': len(text)
        }