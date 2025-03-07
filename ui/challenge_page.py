import streamlit as st
from ui.common import display_header, display_success_message
from database.quiz_db import get_quiz_sets, get_quiz_questions
from database.challenge_db import save_challenge
from services.openai_service import generate_questions_with_openai

def handle_back_to_menu():
    """Handle back to menu button click"""
    st.session_state.page = 'menu'
    st.session_state.questions = []
    st.rerun()

def display_challenge_page():
    """Display the challenge creation page"""
    display_header("Create Challenge", f"Set Number: {st.session_state.set_number}")
    
    # Challenge name
    st.subheader("Challenge Name")
    challenge_name = st.text_input("Enter challenge name")
    
    # Prerequisite selection
    st.subheader("Select Prerequisites")
    st.write("Choose at least 2 prerequisite quiz sets:")
    
    quiz_sets = get_quiz_sets()
    if not quiz_sets:
        st.warning("No quiz sets available. Please create some quizzes first.")
        if st.button("Back to Menu"):
            handle_back_to_menu()
        return
    
    # Allow the user to select multiple quiz sets
    selected_sets = []
    for quiz in quiz_sets:
        if st.checkbox(f"Set {quiz['set_number']}: {quiz['subject_name']} - {quiz['topic_name']}", key=f"set_{quiz['id']}"):
            selected_sets.append(quiz)
    
    # Display questions from selected sets
    if len(selected_sets) < 2:
        st.warning("Please select at least 2 prerequisite quiz sets.")
    else:
        selected_set_ids = [s['id'] for s in selected_sets]
        prerequisite_questions = get_quiz_questions(selected_set_ids)
        
        if prerequisite_questions:
            with st.expander("View Prerequisite Questions"):
                for q in prerequisite_questions:
                    st.markdown(f"**Set {q['set_number']}, Question {q['question_number']}**: {q['question_text']}")
                    for opt, text in q['options'].items():
                        if opt == q['correct_answer']:
                            st.markdown(f"* **{opt}: {text} ✓**")
                        else:
                            st.markdown(f"* {opt}: {text}")
                    st.markdown(f"**Reason**: {q['reason']}")
                    st.markdown("---")
            
            # Generate harder questions
            if st.button("Generate Harder Questions"):
                # Combine questions for context
                context = ""
                for q in prerequisite_questions:
                    context += f"Question: {q['question_text']}\n"
                    for opt, text in q['options'].items():
                        context += f"{opt}: {text}\n"
                    context += f"Answer: {q['correct_answer']}\n"
                    context += f"Reason: {q['reason']}\n\n"
                
                with st.spinner("Generating harder questions based on prerequisites..."):
                    st.session_state.questions = generate_questions_with_openai(context, question_type="challenge")
                    if st.session_state.questions:
                        st.success("Challenge questions generated successfully!")
        else:
            st.warning("Could not find questions for the selected prerequisite sets.")
    
    # Display and edit challenge questions
    if st.session_state.questions:
        st.subheader("Review and Edit Challenge Questions")
        
        edited_questions = []
        
        for i, q in enumerate(st.session_state.questions):
            with st.expander(f"Question {i+1}"):
                question_text = st.text_area(f"Question Text", q['question'], key=f"cq_{i}")
                
                options = {}
                for opt in ['A', 'B', 'C', 'D']:
                    if opt in q['options']:
                        options[opt] = st.text_input(f"Option {opt}", q['options'][opt], key=f"copt_{i}_{opt}")
                    else:
                        options[opt] = st.text_input(f"Option {opt}", "", key=f"copt_{i}_{opt}")
                
                answer = st.selectbox(
                    "Correct Answer", 
                    ['A', 'B', 'C', 'D'], 
                    index=['A', 'B', 'C', 'D'].index(q['answer']) if q['answer'] in ['A', 'B', 'C', 'D'] else 0,
                    key=f"cans_{i}"
                )
                reason = st.text_area("Reason", q.get('reason', ''), key=f"creason_{i}")
                
                edited_questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': answer,
                    'reason': reason
                })
        
        # Save all questions
        if challenge_name and edited_questions and len(selected_sets) >= 2:
            if st.button("Save Challenge"):
                # Save to database
                success = save_challenge(
                    st.session_state.set_number, 
                    st.session_state.user['id'],
                    challenge_name, 
                    [s['id'] for s in selected_sets], 
                    edited_questions
                )
                
                if success:
                    display_success_message("Challenge saved successfully!")
                    st.session_state.questions = []
                    st.session_state.set_number = None
                    
                    if st.button("Return to Menu"):
                        handle_back_to_menu()
    
    # Back button
    if st.button("Back to Menu"):
        handle_back_to_menu()