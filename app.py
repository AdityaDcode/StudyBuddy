import streamlit as st
import os
from utils.pdf_processor import PDFProcessor
from utils.gemini_client import GeminiClient
from utils.quiz_generator import QuizGenerator
from utils.chat_manager import ChatManager


st.set_page_config(
    page_title="Smart Study Buddy",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #ffb347 0%, #ffcc33 100%); /* warmer, more natural gradient */
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
    color: #333; /* soft dark text instead of stark white */
    font-family: 'Segoe UI', sans-serif;
}

.feature-card-container {
    display: flex;
    flex-wrap: wrap; /* wrap to next line on smaller screens */
    gap: 1rem;       /* spacing between cards */
    justify-content: center; /* center horizontally */
    margin: 1rem 0;
}

.feature-card {
    background: #fff7f0; /* soft peach tone */
    padding: 0.8rem 1rem; /* smaller padding */
    border-radius: 10px;
    border-left: 4px solid #ffb347; /* accent color */
    box-shadow: 0 1.5px 4px rgba(0,0,0,0.06); /* subtle shadow */
    flex: 1 1 200px; /* responsive width, min 200px */
    max-width: 250px; /* prevent cards from being too wide */
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.1);
}

.feature-card h3 {
    font-size: 1rem;
    margin-bottom: 0.3rem;
    color: #2c3e50;
}

.feature-card p {
    font-size: 0.85rem;
    color: #555;
    margin: 0;
}


.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.4;
}

.user-message {
    background-color: #d1f4ff; /* soft sky blue */
    margin-left: 2rem;
}

.ai-message {
    background-color: #e6f9f0; /* soft mint green */
    margin-right: 2rem;
}

.quiz-container {
    background: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12); /* slightly stronger shadow for depth */
    margin: 1rem 0;
    border: 1px solid #f0f0f0; /* subtle border for separation */
}

</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
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
    
    initialize_session_state()
    

    api_key = "AIzaSyDax4YAYQpefwYh-3Cfuada-nkCqbR6EJk"
    
    pdf_processor = PDFProcessor()
    gemini_client = GeminiClient(api_key)
    quiz_generator = QuizGenerator(gemini_client)
    chat_manager = ChatManager(gemini_client)
    
    
    st.markdown("""
    <div class="main-header">
        <h1>Smart Study Buddy</h1>
        <p>AI-Powered PDF Chat & Quiz Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    with st.sidebar:
        st.header("Upload Your Study Material")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload your class notes, textbooks, or study materials"
        )
        
        if uploaded_file is not None:
            
            if (not st.session_state.pdf_processed or 
                st.session_state.uploaded_file_name != uploaded_file.name):
                
                with st.spinner("Processing PDF..."):
                    try:
                        
                        pdf_text = pdf_processor.extract_text(uploaded_file)
                        st.session_state.pdf_text = pdf_text
                        st.session_state.pdf_processed = True
                        st.session_state.uploaded_file_name = uploaded_file.name
                        
                        
                        st.success("PDF processed successfully!")
                        
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        st.session_state.pdf_processed = False
            
            
            if st.session_state.pdf_processed:
                st.success("PDF ready!")
                st.info(f"Extracted {len(st.session_state.pdf_text.split())} words")
                
                
                with st.expander("Text Preview"):
                    st.text_area(
                        "First 500 characters:",
                        st.session_state.pdf_text[:500] + "..." if len(st.session_state.pdf_text) > 500 else st.session_state.pdf_text,
                        height=200,
                        disabled=True
                    )
        
        
        if st.button("Clear Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.rerun()
    
    
    if st.session_state.pdf_text:
        
        tab1, tab2, tab3 = st.tabs(["Chat with PDF", "Generate Quiz", "Quiz Results"])
        
        with tab1:
            chat_interface(chat_manager)
        
        with tab2:
            quiz_interface(quiz_generator)
        
        with tab3:
            quiz_results_interface()
    
    else:
        
        welcome_screen()

def welcome_screen():
    """Display welcome screen when no PDF is uploaded"""
    

    st.markdown("<h1 style='text-align:center; color:#333;'>Welcome to Smart Study Buddy!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-size:1rem;'>Transform your study experience with AI-powered learning tools.</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top:2rem; margin-bottom:1rem;'>Features</h3>", unsafe_allow_html=True)
    
    
    features = [
        ("PDF Processing", "Upload and extract text from your study materials"),
        ("AI Chat", "Ask questions about your PDF content and get instant answers"),
        ("Quiz Generation", "Generate custom quizzes to test your knowledge"),
        ("Progress Tracking", "Track your quiz performance and learning progress")
    ]
    
    
    cols = st.columns(len(features))
    
    
    card_style = """
        style="
            margin-bottom: 1rem; 
            min-height: 150px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center;
            background: #fff7f0; 
            border-left: 5px solid #ffb347; 
            border-radius:12px;
            padding:1rem;
            text-align:center;"
    """
    
    for i, (title, description) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div {card_style}>
                <h4 style="color:#ff8c42;">{title}</h4>
                <p style="color:#555; font-size:0.95rem;">{description}</p>
            </div>
            """, unsafe_allow_html=True)

def chat_interface(chat_manager):
    """Chat interface for interacting with PDF content"""
    st.header("Chat with Your PDF")
    
    
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
    
    
    user_question = st.text_input(
        "Ask a question about your PDF:",
        placeholder="e.g., What are the main concepts discussed in chapter 3?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Send", type="primary"):
            if user_question.strip():
                
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = chat_manager.get_response(
                            user_question, 
                            st.session_state.pdf_text
                        )
                        
                        
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f" Error getting response: {str(e)}")
    
    with col2:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

def quiz_interface(quiz_generator):
    """Quiz generation and taking interface"""
    st.header("Generate Quiz from Your PDF")

    
    st.text("MCQs and Short Answers")  

    
    num_questions = st.slider(
        "Number of Questions:",
        min_value=3,
        max_value=10,
        value=5,
        help="Select how many questions to generate"
    )

    if st.button("Generate Quiz", type="primary"):
        with st.spinner("Generating quiz questions..."):
            try:
                
                num_mcq = num_questions // 2
                num_short = num_questions - num_mcq

                
                mcq_questions = quiz_generator.generate_quiz(
                    st.session_state.pdf_text,
                    quiz_type='multiple_choice',
                    num_questions=num_mcq
                )

                
                short_questions = quiz_generator.generate_quiz(
                    st.session_state.pdf_text,
                    quiz_type='short_answer',
                    num_questions=num_short
                )

                
                all_questions = mcq_questions + short_questions

                
                st.session_state.quiz_questions = all_questions
                st.session_state.current_quiz_index = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_score = 0

                st.success(f"Generated {len(all_questions)} questions ({num_mcq} MCQs + {num_short} Short Answers)!")

            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")

    
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
        
        
        if question['type'] == 'multiple_choice':
            answer = st.radio(
                "Choose your answer:",
                question['options'],
                key=f"q_{current_index}"
            )
            
            if st.button("Submit Answer", key=f"submit_{current_index}"):
                st.session_state.quiz_answers[current_index] = answer
                
                
                if answer == question['correct_answer']:
                    st.success("Correct!")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f" Incorrect. The correct answer is: {question['correct_answer']}")
                
                
                if 'explanation' in question:
                    st.info(f"Explanation: {question['explanation']}")
                
                
                st.session_state.current_quiz_index += 1
                st.rerun()
        
        else:  
            answer = st.text_area(
                "Your answer:",
                key=f"q_{current_index}",
                height=100
            )
            
            if st.button("Submit Answer ", key=f"submit_{current_index}"):
                st.session_state.quiz_answers[current_index] = answer
                
                
                st.info(f"Expected answer: {question['expected_answer']}")
                
                
                st.session_state.current_quiz_index += 1
                st.rerun()
    
    else:
        
        st.balloons()
        st.success(" Quiz Completed!")
        
        
        mc_questions = [q for q in questions if q['type'] == 'multiple_choice']
        if mc_questions:
            percentage = (st.session_state.quiz_score / len(mc_questions)) * 100
            st.metric("Your Score", f"{st.session_state.quiz_score}/{len(mc_questions)}", f"{percentage:.1f}%")
        
        if st.button("Retake Quiz"):
            st.session_state.current_quiz_index = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = 0
            st.rerun()

def quiz_results_interface():
    """Display quiz results and analytics"""
    st.header("Quiz Results & Progress")
    
    if st.session_state.quiz_questions and st.session_state.quiz_answers:
        
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
        
        
        st.subheader("📝 Detailed Results")
        
        for i, question in enumerate(st.session_state.quiz_questions):
            if i in st.session_state.quiz_answers:
                with st.expander(f"Question {i + 1}: {question['question'][:50]}..."):
                    st.write(f"**Question:** {question['question']}")
                    st.write(f"**Your Answer:** {st.session_state.quiz_answers[i]}")
                    
                    if question['type'] == 'multiple_choice':
                        st.write(f"**Correct Answer:** {question['correct_answer']}")
                        is_correct = st.session_state.quiz_answers[i] == question['correct_answer']
                        st.write(f"**Result:** {'Correct' if is_correct else ' Incorrect'}")
                    else:
                        st.write(f"**Expected Answer:** {question['expected_answer']}")
                    
                    if 'explanation' in question:
                        st.write(f"**Explanation:** {question['explanation']}")
    
    else:
        st.info("Complete a quiz to see your results here!")
        
        
        st.markdown("""
        <div class="feature-card">
            <h3> Study Tips</h3>
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