import streamlit as st
from ui.common import display_header, display_success_message
from database.quiz_db import get_subjects, create_subject, get_topics, create_topic, save_quiz
from services.ppt_service import extract_text_from_pptx
from services.openai_service import generate_questions_with_openai

def handle_back_to_menu():
    """Handle back to menu button click"""
    st.session_state.page = 'menu'
    st.session_state.questions = []
    st.rerun()

def display_quiz_page():
    """Display the quiz creation page"""
    # Display header with set number
    display_header("Create Quiz", f"Set Number: {st.session_state.set_number}")
    
    # Subject selection
    st.subheader("Subject")
    
    # Get subjects from the database
    subjects = get_subjects()
    subject_names = [s['name'] for s in subjects] + ["Add New Subject"]
    
    subject_option = st.selectbox("Select or add a subject", subject_names)
    
    subject_id = None
    
    if subject_option == "Add New Subject":
        new_subject = st.text_input("Enter new subject name")
        if new_subject and st.button("Add Subject"):
            subject_id = create_subject(new_subject)
            if subject_id:
                st.success(f"Subject '{new_subject}' added successfully!")
                st.rerun()
    else:
        # Find the selected subject in the list
        for s in subjects:
            if s['name'] == subject_option:
                subject_id = s['id']
                break
    
    # Topic selection (only if a subject is selected)
    topic_id = None
    if subject_id:
        st.subheader("Topic")
        
        # Get topics for the selected subject
        topics = get_topics(subject_id)
        topic_names = [t['name'] for t in topics] + ["Add New Topic"]
        
        topic_option = st.selectbox("Select or add a topic", topic_names)
        
        if topic_option == "Add New Topic":
            new_topic = st.text_input("Enter new topic name")
            if new_topic and st.button("Add Topic"):
                topic_id = create_topic(subject_id, new_topic)
                if topic_id:
                    st.success(f"Topic '{new_topic}' added successfully!")
                    st.rerun()
        else:
            # Find the selected topic in the list
            for t in topics:
                if t['name'] == topic_option:
                    topic_id = t['id']
                    break
    
    # PowerPoint upload and processing
    if subject_id and topic_id:
        st.subheader("Upload PowerPoint Presentation")
        uploaded_file = st.file_uploader("Choose a PowerPoint file", type="pptx")
        
        if uploaded_file:
            # Extract content from the PowerPoint
            with st.spinner("Processing PowerPoint content..."):
                ppt_content = extract_text_from_pptx(uploaded_file)
                
                if ppt_content:
                    st.success("PowerPoint processed successfully!")
                    
                    with st.expander("View Slide Content"):
                        st.text_area("Content extracted from slides", ppt_content, height=200)
                    
                    # Generate questions
                    if st.button("Generate Questions"):
                        with st.spinner("Generating questions with AI..."):
                            st.session_state.questions = generate_questions_with_openai(ppt_content)
                            if st.session_state.questions:
                                st.success("Questions generated successfully!")
    
    # Display and edit questions
    if st.session_state.questions:
        st.subheader("Review and Edit Questions")
        
        edited_questions = []
        
        for i, q in enumerate(st.session_state.questions):
            with st.expander(f"Question {i+1}"):
                question_text = st.text_area(f"Question Text", q['question'], key=f"q_{i}")
                
                options = {}
                for opt in ['A', 'B', 'C', 'D']:
                    if opt in q['options']:
                        options[opt] = st.text_input(f"Option {opt}", q['options'][opt], key=f"opt_{i}_{opt}")
                    else:
                        options[opt] = st.text_input(f"Option {opt}", "", key=f"opt_{i}_{opt}")
                
                answer = st.selectbox(
                    "Correct Answer", 
                    ['A', 'B', 'C', 'D'], 
                    index=['A', 'B', 'C', 'D'].index(q['answer']) if q['answer'] in ['A', 'B', 'C', 'D'] else 0,
                    key=f"ans_{i}"
                )
                reason = st.text_area("Reason", q.get('reason', ''), key=f"reason_{i}")
                
                edited_questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': answer,
                    'reason': reason
                })
        
        # Save all questions
        if edited_questions and st.button("Save Quiz"):
            # Save to database
            success = save_quiz(
                st.session_state.set_number, 
                st.session_state.user['id'],
                subject_id, 
                topic_id, 
                edited_questions
            )
            
            if success:
                display_success_message("Quiz saved successfully!")
                st.session_state.questions = []
                st.session_state.set_number = None
                
                if st.button("Return to Menu"):
                    handle_back_to_menu()
    
    # Back button
    if st.button("Back to Menu"):
        handle_back_to_menu()