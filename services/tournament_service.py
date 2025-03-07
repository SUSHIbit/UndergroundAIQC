import openai
import streamlit as st
from datetime import datetime, timedelta
import random
import json

def generate_tournament_with_openai(description=""):
    """
    Generate tournament details using OpenAI
    
    Args:
        description (str): Optional user description for the tournament
    
    Returns:
        dict: Tournament details
    """
    try:
        # Default description for web design competition if not provided
        if not description:
            description = "A web design competition for university students where they need to redesign a website for a fictitious cat company."
            
        prompt = f"""
        Generate detailed information for a web design tournament for university students based on the following description:
        {description}
        
        The tournament should be for a fictitious cat company called "Purr-fect Designs" that wants to redesign their website.
        
        Please provide the following details in a structured format:
        1. Title (creative and engaging)
        2. Description (detailed, include the company background and what they're looking for)
        3. Date and Time (a future date)
        4. Location (both virtual and a physical location at a university)
        5. Eligibility requirements (who can participate)
        6. Minimum rank required (choose from: Unranked, Bronze, Silver, Gold, Master, Grand Master, One Above All)
        7. Team size (between 1-4)
        8. Submission deadline (before the tournament date)
        9. Tournament rules (detailed)
        10. Judging criteria (be specific about design, usability, creativity, etc.)
        11. Project submission guidelines (what needs to be submitted and how)
        12. List of judges (3-5 judges with name and role)
        
        Format the response as JSON to be easily parsed.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tournament planning assistant that creates detailed web design competitions for university students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                tournament_data = json.loads(json_str)
            else:
                # If JSON format is not detected, parse manually
                tournament_data = parse_tournament_response(response_text)
        except Exception as e:
            st.error(f"Error parsing OpenAI response: {e}")
            # Fallback to manual parsing
            tournament_data = parse_tournament_response(response_text)
        
        # Ensure we have all the required fields
        return ensure_tournament_fields(tournament_data)
        
    except Exception as e:
        st.error(f"Error generating tournament: {e}")
        # Return default tournament data as fallback
        return generate_default_tournament()

def parse_tournament_response(response_text):
    """Parse the OpenAI response into a structured tournament object"""
    lines = response_text.strip().split('\n')
    tournament_data = {}
    current_field = None
    current_content = []
    
    # Define the fields we're looking for
    fields = {
        "title": ["title"],
        "description": ["description"],
        "date_time": ["date", "time", "date and time"],
        "location": ["location"],
        "eligibility": ["eligibility"],
        "minimum_rank": ["minimum rank"],
        "team_size": ["team size"],
        "deadline": ["deadline", "submission deadline"],
        "rules": ["rules", "tournament rules"],
        "judging_criteria": ["judging criteria"],
        "project_submission": ["project submission", "submission guidelines"],
        "judges": ["judges", "list of judges"]
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a field header
        found_field = None
        for field, keywords in fields.items():
            for keyword in keywords:
                if line.lower().startswith(f"{keyword}:") or line.lower().startswith(f"{keyword.title()}:"):
                    if current_field and current_content:
                        tournament_data[current_field] = "\n".join(current_content).strip()
                    found_field = field
                    current_field = field
                    current_content = [line.split(":", 1)[1].strip()]
                    break
            if found_field:
                break
                
        if not found_field and current_field:
            current_content.append(line)
    
    # Add the last field
    if current_field and current_content:
        tournament_data[current_field] = "\n".join(current_content).strip()
    
    return tournament_data

def ensure_tournament_fields(tournament_data):
    """Ensure all required fields are present in tournament data"""
    default_tournament = generate_default_tournament()
    
    # Make sure all required fields exist
    for key in default_tournament:
        if key not in tournament_data or not tournament_data[key]:
            tournament_data[key] = default_tournament[key]
    
    # Special processing for judges
    if isinstance(tournament_data["judges"], str):
        # Convert string to list of dictionaries
        judges_text = tournament_data["judges"]
        judges = []
        lines = judges_text.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                name = parts[0].strip()
                role = parts[1].strip() if len(parts) > 1 else "Judge"
                judges.append({"name": name, "role": role})
            elif line.strip():
                judges.append({"name": line.strip(), "role": "Judge"})
        
        if not judges:
            judges = default_tournament["judges"]
        
        tournament_data["judges"] = judges
    
    # Special processing for dates
    if isinstance(tournament_data["date_time"], str):
        try:
            # Try to parse the date
            date_str = tournament_data["date_time"]
            # Very flexible date parsing would go here
            # For simplicity, we'll use a default date if parsing fails
            tournament_data["date_time"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["date_time"] = default_tournament["date_time"]
    
    if isinstance(tournament_data["deadline"], str):
        try:
            # Try to parse the deadline
            deadline_str = tournament_data["deadline"]
            # Very flexible date parsing would go here
            # For simplicity, we'll use a default date if parsing fails
            tournament_data["deadline"] = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["deadline"] = default_tournament["deadline"]
    
    return tournament_data

def generate_default_tournament():
    """Generate default tournament data as fallback"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Purr-fect Web Design Challenge",
        "description": "Join the Purr-fect Web Design Challenge and showcase your creativity in redesigning the website for Purr-fect Designs, a leading cat product company. This competition challenges university students to create an innovative, user-friendly website that captures the essence of the feline-focused brand while implementing modern web design principles.",
        "date_time": tournament_date,
        "location": "Virtual event + University Main Auditorium",
        "eligibility": "Open to all university students with an interest in web design and development. Participants must be currently enrolled in an undergraduate or graduate program.",
        "minimum_rank": "Bronze",
        "team_size": 3,
        "deadline": submission_deadline,
        "rules": "1. All submissions must be original work.\n2. Designs must be responsive and work on mobile devices.\n3. Submissions must include at least 5 pages (home, about, products, contact, and blog).\n4. Teams must use HTML, CSS, and JavaScript for their implementation.\n5. Use of frameworks like React, Vue, or Angular is permitted.\n6. Submissions must be accessible and follow WCAG guidelines.\n7. All assets used must be original or properly licensed.",
        "judging_criteria": "1. Visual Design (30%): Aesthetics, color scheme, typography, and overall visual appeal.\n2. User Experience (25%): Navigation, information architecture, and ease of use.\n3. Technical Implementation (20%): Code quality, performance, and proper implementation.\n4. Creativity (15%): Originality and innovative approach to the brand.\n5. Accessibility (10%): Compliance with accessibility standards.",
        "project_submission": "Teams must submit:\n1. A GitHub repository with all source code.\n2. A working URL where the website is deployed.\n3. A brief (500 words max) design document explaining the concept and implementation.\n4. A 3-minute video walkthrough of the website highlighting key features.",
        "judges": [
            {"name": "Professor Emma Chen", "role": "Department of Design Head"},
            {"name": "Michael Rodriguez", "role": "Senior UX Designer at TechCorp"},
            {"name": "Sarah Patel", "role": "Frontend Development Expert"},
            {"name": "Dr. James Wilson", "role": "Web Accessibility Specialist"}
        ]
    }

def generate_web_design_tournament():
    """Generate a web design tournament with a cat company theme"""
    cat_companies = [
        "Purr-fect Designs", "Whisker Web Solutions", "Meow Marketing", 
        "Feline Frameworks", "Cat-alog Designs", "The Furry Site Co.",
        "Paws & Pixels", "9Lives Digital", "CatNip Creative"
    ]
    
    company_name = random.choice(cat_companies)
    
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": f"{company_name} Website Redesign Challenge",
        "description": f"Design a modern, user-friendly website for {company_name}, a fictional cat-focused company looking to improve their online presence. The company specializes in premium cat products and needs a website that appeals to cat owners and showcases their unique brand identity.",
        "date_time": tournament_date,
        "location": "Virtual event + University Design Lab",
        "eligibility": "Open to all university students studying web design, computer science, graphic design, or related fields.",
        "minimum_rank": "Bronze",
        "team_size": 2,
        "deadline": submission_deadline,
        "rules": f"1. Create a complete responsive website for {company_name}.\n2. All code and design assets must be original or properly licensed.\n3. Website must include at least 5 main pages.\n4. Designs must be optimized for both desktop and mobile devices.\n5. Teams must use modern web technologies and follow best practices.",
        "judging_criteria": "1. Visual Design (30%): Brand alignment, aesthetics, and visual appeal.\n2. User Experience (25%): Intuitive navigation and overall usability.\n3. Technical Execution (20%): Code quality and performance.\n4. Creativity and Innovation (15%): Original ideas and unique approaches.\n5. Presentation (10%): How well the solution is presented and explained.",
        "project_submission": "Submit a GitHub repository link containing all code, a live demo URL, and a presentation PDF explaining your design choices.",
        "judges": [
            {"name": "Alex Morgan", "role": "Senior Web Designer"},
            {"name": "Dr. Priya Sharma", "role": "Professor of Digital Media"},
            {"name": "Jason Chen", "role": "UX Research Lead"},
            {"name": "Olivia Thompson", "role": "Frontend Developer"}
        ]
    }