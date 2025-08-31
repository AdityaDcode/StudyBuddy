import streamlit as st
import os
from utils.pdf_processor import PDFProcessor
from utils.gemini_client import GeminiClient
from utils.quiz_generator import QuizGenerator
from utils.chat_manager import ChatManager

# Page configuration
st.set_page_config(
    page_title="Smart Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .ai-message {
        background-color: #f1f8e9;
        margin-right: 2rem;
    }
    
    .quiz-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_quiz_index' not in st.session_state:
        st.session_state.current_quiz_index = 0
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Initialize components with API key
    api_key = "AIzaSyDax4YAYQpefwYh-3Cfuada-nkCqbR6EJk"
    
    pdf_processor = PDFProcessor()
    gemini_client = GeminiClient(api_key)
    quiz_generator = QuizGenerator(gemini_client)
    chat_manager = ChatManager(gemini_client)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📚 Smart Study Buddy</h1>
        <p>AI-Powered PDF Chat & Quiz Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for PDF upload and settings
    with st.sidebar:
        st.header("📄 Upload Your Study Material")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload your class notes, textbooks, or study materials"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing PDF..."):
                try:
                    # Process the uploaded PDF
                    pdf_text = pdf_processor.extract_text(uploaded_file)
                    st.session_state.pdf_text = pdf_text
                    
                    # Display PDF info
                    st.success("✅ PDF processed successfully!")
                    st.info(f"📊 Extracted {len(pdf_text.split())} words")
                    
                    # Show preview of extracted text
                    with st.expander("📖 Text Preview"):
                        st.text_area(
                            "First 500 characters:",
                            pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text,
                            height=200,
                            disabled=True
                        )
                        
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
        
        # Clear session button
        if st.button("🔄 Clear Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    if st.session_state.pdf_text:
        # Create tabs for different features
        tab1, tab2, tab3 = st.tabs(["💬 Chat with PDF", "🧠 Generate Quiz", "📊 Quiz Results"])
        
        with tab1:
            chat_interface(chat_manager)
        
        with tab2:
            quiz_interface(quiz_generator)
        
        with tab3:
            quiz_results_interface()
    
    else:
        # Welcome screen when no PDF is uploaded
        welcome_screen()

def welcome_screen():
    """Display welcome screen when no PDF is uploaded"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h2>🎯 Welcome to Smart Study Buddy!</h2>
            <p>Transform your study experience with AI-powered learning tools.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("### ✨ Features")
        
        features = [
            ("📄 PDF Processing", "Upload and extract text from your study materials"),
            ("💬 AI Chat", "Ask questions about your PDF content and get instant answers"),
            ("🧠 Quiz Generation", "Generate custom quizzes to test your knowledge"),
            ("📊 Progress Tracking", "Track your quiz performance and learning progress")
        ]
        
        for title, description in features:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Get Started")
        st.info("👈 Upload a PDF file in the sidebar to begin your AI-powered study session!")

def chat_interface(chat_manager):
    """Chat interface for interacting with PDF content"""
    st.header("💬 Chat with Your PDF")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_question = st.text_input(
        "Ask a question about your PDF:",
        placeholder="e.g., What are the main concepts discussed in chapter 3?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Send 📤", type="primary"):
            if user_question.strip():
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                # Get AI response
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = chat_manager.get_response(
                            user_question, 
                            st.session_state.pdf_text
                        )
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error getting response: {str(e)}")
    
    with col2:
        if st.button("Clear Chat 🗑️", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

def quiz_interface(quiz_generator):
    """Quiz generation and taking interface"""
    st.header("🧠 Generate Quiz from Your PDF")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        quiz_type = st.selectbox(
            "Select Quiz Type:",
            ["Multiple Choice", "Short Answer", "Mixed"],
            help="Choose the type of quiz you want to generate"
        )
    
    with col2:
        num_questions = st.slider(
            "Number of Questions:",
            min_value=3,
            max_value=10,
            value=5,
            help="Select how many questions to generate"
        )
    
    if st.button("🎯 Generate Quiz", type="primary"):
        with st.spinner("🎲 Generating quiz questions..."):
            try:
                questions = quiz_generator.generate_quiz(
                    st.session_state.pdf_text,
                    quiz_type.lower().replace(" ", "_"),
                    num_questions
                )
                
                st.session_state.quiz_questions = questions
                st.session_state.current_quiz_index = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_score = 0
                
                st.success(f"✅ Generated {len(questions)} questions!")
                
            except Exception as e:
                st.error(f"❌ Error generating quiz: {str(e)}")
    
    # Display quiz questions if available
    if st.session_state.quiz_questions:
        display_quiz()

def display_quiz():
    """Display and handle quiz questions"""
    questions = st.session_state.quiz_questions
    current_index = st.session_state.current_quiz_index
    
    if current_index < len(questions):
        question = questions[current_index]
        
        st.markdown(f"""
        <div class="quiz-container">
            <h3>Question {current_index + 1} of {len(questions)}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**{question['question']}**")
        
        # Handle different question types
        if question['type'] == 'multiple_choice':
            answer = st.radio(
                "Choose your answer:",
                question['options'],
                key=f"q_{current_index}"
            )
            
            if st.button("Submit Answer ✅", key=f"submit_{current_index}"):
                st.session_state.quiz_answers[current_index] = answer
                
                # Check if answer is correct
                if answer == question['correct_answer']:
                    st.success("🎉 Correct!")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {question['correct_answer']}")
                
                # Show explanation if available
                if 'explanation' in question:
                    st.info(f"💡 Explanation: {question['explanation']}")
                
                # Move to next question
                st.session_state.current_quiz_index += 1
                st.rerun()
        
        else:  # Short answer
            answer = st.text_area(
                "Your answer:",
                key=f"q_{current_index}",
                height=100
            )
            
            if st.button("Submit Answer ✅", key=f"submit_{current_index}"):
                st.session_state.quiz_answers[current_index] = answer
                
                # For short answers, show the expected answer
                st.info(f"💡 Expected answer: {question['expected_answer']}")
                
                # Move to next question
                st.session_state.current_quiz_index += 1
                st.rerun()
    
    else:
        # Quiz completed
        st.balloons()
        st.success("🎊 Quiz Completed!")
        
        # Calculate score for multiple choice questions
        mc_questions = [q for q in questions if q['type'] == 'multiple_choice']
        if mc_questions:
            percentage = (st.session_state.quiz_score / len(mc_questions)) * 100
            st.metric("Your Score", f"{st.session_state.quiz_score}/{len(mc_questions)}", f"{percentage:.1f}%")
        
        if st.button("🔄 Retake Quiz"):
            st.session_state.current_quiz_index = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = 0
            st.rerun()

def quiz_results_interface():
    """Display quiz results and analytics"""
    st.header("📊 Quiz Results & Progress")
    
    if st.session_state.quiz_questions and st.session_state.quiz_answers:
        # Overall statistics
        total_questions = len(st.session_state.quiz_questions)
        answered_questions = len(st.session_state.quiz_answers)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Questions", total_questions)
        
        with col2:
            st.metric("Answered", answered_questions)
        
        with col3:
            if st.session_state.quiz_score > 0:
                mc_questions = [q for q in st.session_state.quiz_questions if q['type'] == 'multiple_choice']
                if mc_questions:
                    percentage = (st.session_state.quiz_score / len(mc_questions)) * 100
                    st.metric("Score", f"{percentage:.1f}%")
        
        # Detailed results
        st.subheader("📝 Detailed Results")
        
        for i, question in enumerate(st.session_state.quiz_questions):
            if i in st.session_state.quiz_answers:
                with st.expander(f"Question {i + 1}: {question['question'][:50]}..."):
                    st.write(f"**Question:** {question['question']}")
                    st.write(f"**Your Answer:** {st.session_state.quiz_answers[i]}")
                    
                    if question['type'] == 'multiple_choice':
                        st.write(f"**Correct Answer:** {question['correct_answer']}")
                        is_correct = st.session_state.quiz_answers[i] == question['correct_answer']
                        st.write(f"**Result:** {'✅ Correct' if is_correct else '❌ Incorrect'}")
                    else:
                        st.write(f"**Expected Answer:** {question['expected_answer']}")
                    
                    if 'explanation' in question:
                        st.write(f"**Explanation:** {question['explanation']}")
    
    else:
        st.info("🎯 Complete a quiz to see your results here!")
        
        # Study tips
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Study Tips</h3>
            <ul>
                <li>Review the PDF content thoroughly before taking quizzes</li>
                <li>Use the chat feature to clarify difficult concepts</li>
                <li>Retake quizzes to reinforce learning</li>
                <li>Focus on areas where you scored lower</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()