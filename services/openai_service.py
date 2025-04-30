import os
import streamlit as st
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_questions_with_openai(content, question_type="quiz", difficulty_level=None):
    """
    Generate questions using OpenAI based on the slide content
    
    Args:
        content (str): The slide content to generate questions from
        question_type (str): Type of questions to generate ("quiz" or "challenge")
        difficulty_level (str, optional): Difficulty level ("Diploma" or "Degree")
    
    Returns:
        list: List of question dictionaries
    """
    try:
        # If difficulty level is specified, use Bloom's Taxonomy for quiz generation
        if question_type == "quiz" and difficulty_level:
            return generate_blooms_taxonomy_questions(content, difficulty_level)
        
        # Default behavior (original functionality)
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

def generate_blooms_taxonomy_questions(content, difficulty_level):
    """
    Generate questions using Bloom's Taxonomy based on difficulty level
    
    Args:
        content (str): The slide content to generate questions from
        difficulty_level (str): Difficulty level ("Diploma" or "Degree")
    
    Returns:
        list: List of question dictionaries
    """
    try:
        all_questions = []
        
        # Define Bloom's levels based on difficulty
        if difficulty_level == "Diploma":
            bloom_levels = ["Remember", "Understand", "Apply"]
        else:  # Degree
            bloom_levels = ["Analyze", "Evaluate", "Create"]
        
        # Generate 10 questions for each Bloom's level
        for level in bloom_levels:
            questions = generate_questions_for_bloom_level(content, level)
            all_questions.extend(questions)
        
        return all_questions
    
    except Exception as e:
        st.error(f"Error generating Bloom's Taxonomy questions: {e}")
        return []

def generate_questions_for_bloom_level(content, bloom_level):
    """
    Generate questions for a specific Bloom's Taxonomy level
    
    Args:
        content (str): The slide content to generate questions from
        bloom_level (str): The Bloom's Taxonomy level
    
    Returns:
        list: List of question dictionaries
    """
    # Descriptions and examples for each Bloom's level
    level_descriptions = {
        "Remember": "Questions that test recall of facts, terms, basic concepts, or answers. Keywords: define, list, memorize, recall, repeat, reproduce, state.",
        "Understand": "Questions that demonstrate understanding of facts and ideas by organizing, comparing, translating, interpreting, giving descriptions, and stating the main ideas. Keywords: classify, describe, discuss, explain, identify, locate, recognize, report, select, translate.",
        "Apply": "Questions that solve problems by applying acquired knowledge, facts, techniques, and rules in a different way. Keywords: apply, build, choose, construct, develop, experiment with, identify, interview, make use of, model, organize, plan, select, solve, utilize.",
        "Analyze": "Questions that examine and break information into parts by identifying motives or causes, making inferences, and finding evidence to support generalizations. Keywords: analyze, assume, categorize, classify, compare, conclusion, contrast, discover, dissect, distinguish, divide, examine, function, inference, inspect, list, motive, relationships, simplify, survey, take part in, test for, theme.",
        "Evaluate": "Questions that present and defend opinions by making judgments about information, the validity of ideas, or quality of work based on a set of criteria. Keywords: agree, appraise, assess, award, choose, compare, conclude, criteria, criticize, decide, deduct, defend, determine, disprove, estimate, evaluate, explain, importance, influence, interpret, judge, justify, mark, measure, opinion, perceive, prioritize, prove, rate, recommend, rule on, select, support, value.",
        "Create": "Questions that compile information together in a different way by combining elements in a new pattern or proposing alternative solutions. Keywords: adapt, build, change, choose, combine, compile, compose, construct, create, delete, design, develop, discuss, elaborate, estimate, formulate, happen, imagine, improve, invent, make up, maximize, minimize, modify, original, originate, plan, predict, propose, solution, solve, suppose, test, theory."
    }
    
    # Craft the prompt with the appropriate Bloom's level description
    prompt = f"""
    Based on the following lecture slide content, generate 10 multiple-choice questions at the "{bloom_level}" level of Bloom's Taxonomy.
    
    {level_descriptions[bloom_level]}
    
    Each question should have 4 options (A, B, C, D) with only one correct answer.
    For each question, also provide:
    1. The correct answer letter
    2. A brief explanation for why that answer is correct
    
    Format each question as follows:
    Question 1: [Question text]
    Options: A: [Option A], B: [Option B], C: [Option C], D: [Option D]
    Answer: [Correct answer letter]
    Reason: [Explanation]
    Bloom Level: {bloom_level}
    
    Only use information that can be derived from the content. All questions MUST be aligned with the "{bloom_level}" level of Bloom's Taxonomy.
    
    Content:
    {content}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are an educational assistant that creates accurate multiple-choice questions based on lecture content. You specialize in creating questions at the {bloom_level} level of Bloom's Taxonomy."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7
    )
    
    response_text = response.choices[0].message.content
    
    # Process response into structured questions
    questions = parse_openai_response(response_text, bloom_level)
    return questions

def parse_openai_response(response_text, bloom_level=None):
    """
    Parse the OpenAI response into structured question objects
    
    Args:
        response_text (str): The raw text response from OpenAI
        bloom_level (str, optional): The Bloom's Taxonomy level for the questions
    
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
                # Add bloom level if provided
                if bloom_level and 'bloom_level' not in current_question:
                    current_question['bloom_level'] = bloom_level
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
            
        elif line.startswith("Bloom Level:"):
            current_question['bloom_level'] = line[12:].strip()
    
    # Add the last question
    if current_question and 'question' in current_question:
        # Add bloom level if provided
        if bloom_level and 'bloom_level' not in current_question:
            current_question['bloom_level'] = bloom_level
        questions.append(current_question)
    
    return questions