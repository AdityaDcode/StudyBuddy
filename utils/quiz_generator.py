import json
import re
import streamlit as st

class QuizGenerator:
    """Handles quiz generation from PDF content"""
    
    def __init__(self, gemini_client):
        """
        Initialize quiz generator
        
        Args:
            gemini_client: Instance of GeminiClient
        """
        self.gemini_client = gemini_client
        self.question_types = {
            'multiple_choice': 'Multiple Choice',
            'short_answer': 'Short Answer',
            'mixed': 'Mixed (Both Types)'
        }
    
    def generate_quiz(self, pdf_content, quiz_type='multiple_choice', num_questions=5):
        """
        Generate quiz questions from PDF content
        
        Args:
            pdf_content (str): Extracted PDF text
            quiz_type (str): Type of quiz to generate
            num_questions (int): Number of questions to generate
            
        Returns:
            list: List of quiz questions
        """
        try:
            # Validate inputs
            if not pdf_content.strip():
                raise ValueError("PDF content is empty")
            
            if num_questions < 1 or num_questions > 10:
                raise ValueError("Number of questions must be between 1 and 10")
            
            # Generate quiz content using Gemini
            quiz_response = self.gemini_client.generate_quiz_content(
                pdf_content, quiz_type, num_questions
            )
            
            # Parse the response to extract questions
            questions = self._parse_quiz_response(quiz_response, quiz_type, num_questions)
            
            return questions
            
        except Exception as e:
            raise Exception(f"Quiz generation failed: {str(e)}")
    
    def _parse_quiz_response(self, response, quiz_type, num_questions):
        """
        Parse AI response to extract quiz questions
        
        Args:
            response (str): Raw AI response
            quiz_type (str): Expected quiz type
            num_questions (int): Expected number of questions
            
        Returns:
            list: Parsed quiz questions
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                questions = json.loads(json_str)
            else:
                # Fallback: create questions from text response
                questions = self._create_fallback_questions(response, quiz_type, num_questions)
            
            # Validate and clean questions
            validated_questions = self._validate_questions(questions, num_questions)
            
            return validated_questions
            
        except json.JSONDecodeError:
            # If JSON parsing fails, create fallback questions
            return self._create_fallback_questions(response, quiz_type, num_questions)
    
    def _validate_questions(self, questions, expected_count):
        """
        Validate and clean quiz questions
        
        Args:
            questions (list): Raw questions from AI
            expected_count (int): Expected number of questions
            
        Returns:
            list: Validated questions
        """
        validated = []
        
        for i, question in enumerate(questions):
            if i >= expected_count:
                break
                
            # Ensure required fields exist
            if 'question' not in question or 'type' not in question:
                continue
            
            # Validate multiple choice questions
            if question['type'] == 'multiple_choice':
                if 'options' not in question or 'correct_answer' not in question:
                    continue
                
                # Ensure we have 4 options
                if len(question['options']) < 2:
                    continue
                
                # Ensure correct answer is in options
                if question['correct_answer'] not in question['options']:
                    question['correct_answer'] = question['options'][0]
            
            # Validate short answer questions
            elif question['type'] == 'short_answer':
                if 'expected_answer' not in question:
                    question['expected_answer'] = "Answer not provided"
            
            validated.append(question)
        
        return validated
    
    def _create_fallback_questions(self, response, quiz_type, num_questions):
        """
        Create fallback questions when parsing fails
        
        Args:
            response (str): AI response text
            quiz_type (str): Quiz type
            num_questions (int): Number of questions needed
            
        Returns:
            list: Fallback questions
        """
        questions = []
        
        # Create simple questions based on the response
        lines = response.split('\n')
        question_lines = [line for line in lines if '?' in line]
        
        for i in range(min(num_questions, len(question_lines), 3)):
            if quiz_type == 'multiple_choice' or quiz_type == 'mixed':
                questions.append({
                    'question': question_lines[i] if i < len(question_lines) else f"What is a key concept from the study material? (Question {i+1})",
                    'type': 'multiple_choice',
                    'options': ['A) Option 1', 'B) Option 2', 'C) Option 3', 'D) Option 4'],
                    'correct_answer': 'A) Option 1',
                    'explanation': 'This is a fallback question due to parsing issues.'
                })
            else:
                questions.append({
                    'question': question_lines[i] if i < len(question_lines) else f"Explain a key concept from the study material. (Question {i+1})",
                    'type': 'short_answer',
                    'expected_answer': 'Please refer to the study material for the complete answer.'
                })
        
        # If no questions generated, create at least one
        if not questions:
            questions.append({
                'question': 'What are the main topics covered in this study material?',
                'type': 'short_answer',
                'expected_answer': 'Please summarize the key topics from the uploaded PDF.'
            })
        
        return questions
    
    def get_quiz_statistics(self, questions, answers):
        """
        Calculate quiz statistics
        
        Args:
            questions (list): Quiz questions
            answers (dict): User answers
            
        Returns:
            dict: Quiz statistics
        """
        total_questions = len(questions)
        answered_questions = len(answers)
        
        # Calculate score for multiple choice questions
        correct_answers = 0
        mc_questions = 0
        
        for i, question in enumerate(questions):
            if question['type'] == 'multiple_choice':
                mc_questions += 1
                if i in answers and answers[i] == question['correct_answer']:
                    correct_answers += 1
        
        accuracy = (correct_answers / mc_questions * 100) if mc_questions > 0 else 0
        completion = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'multiple_choice_questions': mc_questions,
            'correct_answers': correct_answers,
            'accuracy_percentage': accuracy,
            'completion_percentage': completion
        }