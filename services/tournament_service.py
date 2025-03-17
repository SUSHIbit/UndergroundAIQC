import openai
import streamlit as st
from datetime import datetime, timedelta
import random
import json

def generate_tournament_with_openai(description=""):
    """
    Generate tournament details using OpenAI GPT-3.5 Turbo
    
    Args:
        description (str): Optional user description for the tournament
    
    Returns:
        dict: Tournament details
    """
    try:
        # Default description for web design competition if not provided
        if not description:
            description = "A web design competition for university students where they need to redesign a website for a fictional cat company."
            
        prompt = f"""
        Generate detailed information for a web design tournament for university students based on the following description:
        {description}
        
        Please provide the following details in a structured format:
        1. Title (creative and engaging)
        2. Description (detailed, include the company or organization background and what they're looking for)
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
        
        Be creative with the theme and make it engaging for university students. The title should be catchy and related to the theme.
        Format the response as JSON to be easily parsed.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tournament planning assistant that creates detailed creative competitions for university students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8  # Slightly higher temperature for more creativity
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

def generate_creative_web_topics(count=3):
    """
    Generate creative web design tournament topics using GPT-3.5
    
    Args:
        count (int): Number of topics to generate
        
    Returns:
        list: List of topic dictionaries with title and description
    """
    try:
        prompt = f"""
        Generate {count} creative and unique web design tournament topics for university students.
        Each topic should have a different focus and theme.
        
        For each topic, provide:
        1. A catchy title (2-7 words)
        2. A short description (2-3 sentences)
        3. A client description (who the students are designing for)
        4. A key focus area (e.g., UX/UI, e-commerce, accessibility, etc.)
        
        Format the response as a JSON array with objects containing:
        - title: The tournament title
        - description: The short description
        - client: The client description
        - focus: The key focus area
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative director specializing in web design competitions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.9  # Higher temperature for more creative variety
        )
        
        response_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                topics = json.loads(json_str)
            else:
                # Attempt to find a JSON object instead
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    topics = [json.loads(json_str)]
                else:
                    # If no JSON format is detected, create a fallback
                    topics = generate_fallback_topics(count)
        except Exception as e:
            st.error(f"Error parsing topics: {e}")
            topics = generate_fallback_topics(count)
        
        return topics
        
    except Exception as e:
        st.error(f"Error generating topics: {e}")
        return generate_fallback_topics(count)

def generate_fallback_topics(count=3):
    """Generate fallback topics if the API call fails"""
    topics = [
        {
            "title": "Eco-Commerce Challenge",
            "description": "Design an e-commerce website for sustainable products. Focus on highlighting eco-friendly aspects while maintaining excellent user experience.",
            "client": "GreenEarth Co., a startup selling sustainable household products",
            "focus": "E-commerce UX with sustainability focus"
        },
        {
            "title": "Senior-Tech Portal",
            "description": "Create an accessible web portal for elderly users to connect with family. Emphasize simplicity, accessibility, and ease of use.",
            "client": "SilverConnect, a non-profit organization helping seniors stay connected",
            "focus": "Accessibility and inclusive design"
        },
        {
            "title": "Culinary Quest Website",
            "description": "Design a recipe-sharing platform for amateur chefs. Include interactive elements and a visually appealing layout that showcases food photography.",
            "client": "FlavourShare, a community-driven cooking platform",
            "focus": "Visual design and interactive elements"
        },
        {
            "title": "Virtual Museum Experience",
            "description": "Create an immersive online museum that showcases digital art. Focus on creating an engaging virtual space that mimics physical movement through galleries.",
            "client": "DigitalCanvas, an online art collective seeking better exhibition space",
            "focus": "Immersive web experiences and 3D navigation"
        },
        {
            "title": "Pet Adoption Platform",
            "description": "Design a website connecting abandoned pets with potential adopters. Create emotional connections through storytelling while maintaining efficient search functionality.",
            "client": "PawsUnited, a network of animal shelters across the country",
            "focus": "Emotional design and search optimization"
        }
    ]
    
    # Return the requested number of topics
    return topics[:count]

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
        "title": "Creative Web Design Challenge",
        "description": "Join our Creative Web Design Challenge and showcase your skills in designing an innovative, user-friendly website that solves a real-world problem. This competition challenges university students to create a compelling web experience that demonstrates both technical proficiency and creative design thinking.",
        "date_time": tournament_date,
        "location": "Virtual event + University Main Auditorium",
        "eligibility": "Open to all university students with an interest in web design and development. Participants must be currently enrolled in an undergraduate or graduate program.",
        "minimum_rank": "Bronze",
        "team_size": 3,
        "deadline": submission_deadline,
        "rules": "1. All submissions must be original work.\n2. Designs must be responsive and work on mobile devices.\n3. Submissions must include at least 5 pages (home, about, products/services, contact, and one additional page).\n4. Teams must use HTML, CSS, and JavaScript for their implementation.\n5. Use of frameworks and libraries is permitted.\n6. Submissions must be accessible and follow WCAG guidelines.\n7. All assets used must be original or properly licensed.",
        "judging_criteria": "1. Visual Design (30%): Aesthetics, color scheme, typography, and overall visual appeal.\n2. User Experience (25%): Navigation, information architecture, and ease of use.\n3. Technical Implementation (20%): Code quality, performance, and proper implementation.\n4. Creativity (15%): Originality and innovative approach to the design challenge.\n5. Accessibility (10%): Compliance with accessibility standards.",
        "project_submission": "Teams must submit:\n1. A GitHub repository with all source code.\n2. A working URL where the website is deployed.\n3. A brief (500 words max) design document explaining the concept and implementation.\n4. A 3-minute video walkthrough of the website highlighting key features.",
        "judges": [
            {"name": "Professor Emma Chen", "role": "Department of Design Head"},
            {"name": "Michael Rodriguez", "role": "Senior UX Designer at TechCorp"},
            {"name": "Sarah Patel", "role": "Frontend Development Expert"},
            {"name": "Dr. James Wilson", "role": "Web Accessibility Specialist"}
        ]
    }

def generate_web_design_tournament():
    """Generate a web design tournament with a creative theme"""
    # Get creative topics
    topics = generate_creative_web_topics(1)
    topic = topics[0] if topics else {
        "title": "Creative Web Design Challenge",
        "description": "Design an innovative website for a modern business.",
        "client": "A forward-thinking startup",
        "focus": "User experience and visual design"
    }
    
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": topic["title"],
        "description": f"{topic['description']} This competition challenges participants to create a website for {topic['client']} with a focus on {topic['focus']}.",
        "date_time": tournament_date,
        "location": "Virtual event + University Design Lab",
        "eligibility": "Open to all university students studying web design, computer science, graphic design, or related fields.",
        "minimum_rank": "Bronze",
        "team_size": 2,
        "deadline": submission_deadline,
        "rules": f"1. Create a complete responsive website focusing on {topic['focus']}.\n2. All code and design assets must be original or properly licensed.\n3. Website must include at least 5 main pages.\n4. Designs must be optimized for both desktop and mobile devices.\n5. Teams must use modern web technologies and follow best practices.",
        "judging_criteria": "1. Visual Design (30%): Brand alignment, aesthetics, and visual appeal.\n2. User Experience (25%): Intuitive navigation and overall usability.\n3. Technical Execution (20%): Code quality and performance.\n4. Creativity and Innovation (15%): Original ideas and unique approaches.\n5. Presentation (10%): How well the solution is presented and explained.",
        "project_submission": "Submit a GitHub repository link containing all code, a live demo URL, and a presentation PDF explaining your design choices.",
        "judges": [
            {"name": "Alex Morgan", "role": "Senior Web Designer"},
            {"name": "Dr. Priya Sharma", "role": "Professor of Digital Media"},
            {"name": "Jason Chen", "role": "UX Research Lead"},
            {"name": "Olivia Thompson", "role": "Frontend Developer"}
        ]
    }