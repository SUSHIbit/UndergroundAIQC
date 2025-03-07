import os
import streamlit as st
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_questions_with_openai(content, question_type="quiz"):
    """
    Generate questions using OpenAI based on the slide content
    
    Args:
        content (str): The slide content to generate questions from
        question_type (str): Type of questions to generate ("quiz" or "challenge")
    
    Returns:
        list: List of question dictionaries
    """
    try:
        difficulty = "standard" if question_type == "quiz" else "challenging"
        
        prompt = f"""
        Based on the following lecture slide content, generate 10 multiple-choice questions at a {difficulty} difficulty level.
        Each question should have 4 options (A, B, C, D) with only one correct answer.
        For each question, also provide:
        1. The correct answer letter
        2. A brief explanation for why that answer is correct
        
        Format each question as follows:
        Question 1: [Question text]
        Options: A: [Option A], B: [Option B], C: [Option C], D: [Option D]
        Answer: [Correct answer letter]
        Reason: [Explanation]
        
        Only use information explicitly stated in the content. Do not make up information.
        
        Content:
        {content}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational assistant that creates accurate multiple-choice questions based on lecture content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Process response into structured questions
        questions = parse_openai_response(response_text)
        return questions
    
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

def parse_openai_response(response_text):
    """
    Parse the OpenAI response into structured question objects
    
    Args:
        response_text (str): The raw text response from OpenAI
    
    Returns:
        list: List of question dictionaries
    """
    lines = response_text.strip().split('\n')
    questions = []
    current_question = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("Question"):
            # Save previous question if it exists
            if current_question and 'question' in current_question:
                questions.append(current_question)
            
            # Start new question
            q_parts = line.split(":", 1)
            if len(q_parts) > 1:
                current_question = {'question': q_parts[1].strip()}
            else:
                current_question = {'question': ''}
                
        elif line.startswith("Options:"):
            options_str = line[8:].strip()
            options = {}
            for opt in options_str.split(','):
                opt = opt.strip()
                if opt and ':' in opt:
                    key, value = opt.split(':', 1)
                    options[key.strip()] = value.strip()
            current_question['options'] = options
            
        elif line.startswith("Answer:"):
            current_question['answer'] = line[7:].strip()
            
        elif line.startswith("Reason:"):
            current_question['reason'] = line[7:].strip()
    
    # Add the last question
    if current_question and 'question' in current_question:
        questions.append(current_question)
    
    return questions