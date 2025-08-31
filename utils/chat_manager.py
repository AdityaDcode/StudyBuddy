import streamlit as st
import hashlib

class ChatManager:
    """Manages chat functionality and conversation history"""
    
    def __init__(self, gemini_client):
        """
        Initialize chat manager
        
        Args:
            gemini_client: Instance of GeminiClient
        """
        self.gemini_client = gemini_client
        self.max_history_length = 10  # Limit chat history to prevent token overflow
        self.pdf_cache = {}  # Cache for PDF key points
        self.cache_ttl = 3600  # Cache TTL in seconds (1 hour)
    
    def get_response(self, user_question, pdf_content):
        """
        Get AI response to user question with PDF context
        
        Args:
            user_question (str): User's question
            pdf_content (str): PDF text content for context
            
        Returns:
            str: AI-generated response
        """
        try:
            # Validate inputs
            if not user_question.strip():
                raise ValueError("Question cannot be empty")
            
            # Build context from chat history and PDF content
            context = self._build_chat_context(pdf_content)
            
            # Create enhanced prompt with conversation context
            enhanced_prompt = self._create_chat_prompt(user_question, context)
            
            # Get response from Gemini
            response = self.gemini_client.generate_response(enhanced_prompt)
            
            # Clean and format the response
            formatted_response = self._format_response(response)
            
            return formatted_response
            
        except Exception as e:
            raise Exception(f"Failed to get chat response: {str(e)}")
    
    def _extract_key_points(self, pdf_content):
        """
        Extract key points from PDF content and cache them
        
        Args:
            pdf_content (str): Full PDF text content
            
        Returns:
            str: Extracted key points
        """
        # Create a hash of the PDF content for caching
        pdf_hash = hashlib.md5(pdf_content.encode()).hexdigest()
        
        # Check if we have cached key points for this PDF
        if pdf_hash in self.pdf_cache:
            cached_data = self.pdf_cache[pdf_hash]
            return cached_data["key_points"]
        
        
        try:
            prompt = f"""
            Extract the key points, main concepts, and important information from the following document.
            Organize the information in a clear, structured way that would be useful for studying.
            
            Document:
            {pdf_content[:4000]}  # Limit to avoid token limits
            
            Please provide:
            1. Main topics covered
            2. Key concepts and definitions
            3. Important facts or figures
            4. Any notable examples or case studies
            5. Summary of each major section
            
            Format the response in a clear, organized manner.
            """
            
            key_points = self.gemini_client.generate_response(prompt)
            
            # Cache the key points
            self.pdf_cache[pdf_hash] = {
                "key_points": key_points,
            }
            
            return key_points
        except Exception as e:
            # If key point extraction fails, fall back to using truncated PDF content
            return pdf_content[:2000]  # Use less content as fallback
    
    def _build_chat_context(self, pdf_content):
        """
        Build context from PDF content and recent chat history
        
        Args:
            pdf_content (str): PDF text content
            
        Returns:
            str: Combined context
        """
        context_parts = []
        
        # Add PDF key points (cached) instead of full content
        if pdf_content:
            key_points = self._extract_key_points(pdf_content)
            context_parts.append(f"Document Key Points:\n{key_points[:2000]}")  # Limit key points
        
        # Add recent chat history for context
        if st.session_state.chat_history:
            recent_history = st.session_state.chat_history[-6:]  # Last 3 exchanges
            history_text = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in recent_history
            ])
            context_parts.append(f"Recent Conversation:\n{history_text}")
        
        return "\n\n".join(context_parts)
    
    def _create_chat_prompt(self, user_question, context):
        """
        Create a comprehensive chat prompt
        
        Args:
            user_question (str): User's question
            context (str): Combined context
            
        Returns:
            str: Complete prompt for AI
        """
        return f"""
        You are an intelligent study assistant helping a student understand their study material.
        You have access to key points from their uploaded document and conversation history.
        
        Context:
        {context}
        
        Student Question: {user_question}
        
        Instructions:
        - Answer the question based on the provided document key points when possible
        - If the answer isn't in the document, clearly mention this and provide general knowledge
        - Be educational and encouraging in your tone
        - Provide examples and explanations to help understanding
        - If asked about concepts not in the document, explain them clearly
        - Keep responses focused and not too lengthy
        - Use formatting to make responses easy to read
        
        Response:
        """
    
    def _format_response(self, response):
        """
        Format AI response for better readability
        
        Args:
            response (str): Raw AI response
            
        Returns:
            str: Formatted response
        """
        # Basic formatting improvements
        formatted = response.strip()
        
        # Ensure proper spacing after periods
        formatted = re.sub(r'\.(\w)', r'. \1', formatted)
        
        # Clean up excessive whitespace
        formatted = re.sub(r'\n\s*\n\s*\n', '\n\n', formatted)
        
        return formatted
    
    def clear_history(self):
        """Clear chat history"""
        st.session_state.chat_history = []
    
    def clear_cache(self):
        """Clear PDF cache"""
        self.pdf_cache = {}
    
    def get_conversation_summary(self):
        """
        Get a summary of the current conversation
        
        Returns:
            dict: Conversation summary statistics
        """
        history = st.session_state.chat_history
        
        user_messages = [msg for msg in history if msg['role'] == 'user']
        ai_messages = [msg for msg in history if msg['role'] == 'assistant']
        
        return {
            'total_exchanges': len(user_messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'average_user_message_length': sum(len(msg['content']) for msg in user_messages) / len(user_messages) if user_messages else 0,
            'average_ai_message_length': sum(len(msg['content']) for msg in ai_messages) / len(ai_messages) if ai_messages else 0
        }
    
    def export_chat_history(self):
        """
        Export chat history as formatted text
        
        Returns:
            str: Formatted chat history
        """
        if not st.session_state.chat_history:
            return "No chat history available."
        
        formatted_history = "# Chat History - Smart Study Buddy\n\n"
        
        for i, message in enumerate(st.session_state.chat_history):
            role = "You" if message['role'] == 'user' else "AI Assistant"
            formatted_history += f"## {role}:\n{message['content']}\n\n"
        
        return formatted_history

# Import regex for response formatting
import re