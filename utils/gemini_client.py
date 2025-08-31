import google.generativeai as genai
import streamlit as st

class GeminiClient:
    """Handles interactions with Google Gemini API"""
    
    def __init__(self, api_key):
        """
        Initialize Gemini client
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        self._configure_client()
    
    def _configure_client(self):
        """Configure the Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"❌ Failed to configure Gemini API: {str(e)}")
            raise
    
    def generate_response(self, prompt, context=""):
        """
        Generate response using Gemini API
        
        Args:
            prompt (str): User question or prompt
            context (str): Additional context (e.g., PDF content)
            
        Returns:
            str: Generated response
        """
        try:
            # Construct the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _build_prompt(self, user_prompt, context):
        """
        Build a comprehensive prompt with context
        
        Args:
            user_prompt (str): User's question
            context (str): PDF content or other context
            
        Returns:
            str: Complete prompt for the AI
        """
        if context:
            return f"""
            You are a helpful study assistant. Use the following document content to answer the user's question accurately and comprehensively.
            
            Document Content:
            {context[:4000]}  # Limit context to avoid token limits
            
            User Question: {user_prompt}
            
            Instructions:
            - Answer based primarily on the provided document content
            - If the answer isn't in the document, clearly state that
            - Provide detailed explanations when possible
            - Use examples from the document when relevant
            - Keep your response clear and educational
            
            Answer:
            """
        else:
            return f"""
            You are a helpful study assistant. Please answer the following question:
            
            {user_prompt}
            
            Provide a clear, educational response.
            """
    
    def generate_quiz_content(self, text_content, quiz_type, num_questions):
        """
        Generate quiz questions from text content
        
        Args:
            text_content (str): Source text for quiz generation
            quiz_type (str): Type of quiz (multiple_choice, short_answer, mixed)
            num_questions (int): Number of questions to generate
            
        Returns:
            str: Generated quiz content in JSON format
        """
        prompt = self._build_quiz_prompt(text_content, quiz_type, num_questions)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    def _build_quiz_prompt(self, content, quiz_type, num_questions):
        """
        Build prompt for quiz generation
        
        Args:
            content (str): Source content
            quiz_type (str): Type of quiz
            num_questions (int): Number of questions
            
        Returns:
            str: Complete quiz generation prompt
        """
        return f"""
        Create a quiz based on the following educational content. Generate exactly {num_questions} questions.
        
        Content:
        {content[:3000]}  # Limit content to avoid token limits
        
        Quiz Type: {quiz_type}
        
        Instructions:
        - Create {num_questions} questions that test understanding of key concepts
        - For multiple choice questions: provide 4 options (A, B, C, D) with only one correct answer
        - For short answer questions: provide an expected answer
        - Include brief explanations for multiple choice answers
        - Focus on important concepts, not trivial details
        - Make questions challenging but fair
        
        Return the quiz in this EXACT JSON format:
        [
            {{
                "question": "Question text here",
                "type": "multiple_choice",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explanation": "Explanation of why this is correct"
            }},
            {{
                "question": "Question text here",
                "type": "short_answer",
                "expected_answer": "Expected answer here"
            }}
        ]
        
        Generate the quiz now:
        """