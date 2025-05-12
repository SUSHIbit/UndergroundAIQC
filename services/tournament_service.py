import openai
import streamlit as st
from datetime import datetime, timedelta
import random
import json

def generate_tournament_with_openai(description="", tournament_type="web_design"):
    """Generate tournament details using OpenAI GPT-3.5 Turbo
    
    Args:
        description (str): Optional user description for the tournament
        tournament_type (str): Type of tournament (web_design, hackathon, etc.)
        
    Returns:
        dict: Tournament details
    """
    try:
        # Default description for tournament types if not provided
        if not description:
            if tournament_type == "web_design":
                description = "A web design competition for a cat café that's struggling to attract customers and needs a fresh website to showcase their unique offerings."
            elif tournament_type == "hackathon":
                description = "A local healthcare provider is seeking innovative solutions to help patients track their medication adherence and needs a 36-hour hackathon to develop prototypes."
            else:
                description = f"A company is looking for talented {tournament_type.replace('_', ' ')} developers to solve a pressing business challenge."
        
        # Build prompt based on tournament type
        if tournament_type == "hackathon":
            prompt = f"""
            Generate detailed information for a hackathon tournament for university students based on the following description:
            {description}
            
            Please provide the following details in a structured format:
            1. Title (creative and engaging, technical-sounding)
            2. Description (written from the POV of the company/organization with the problem - explain their situation, challenges, and what they hope students will create)
            3. Date and Time (a future date, specifically a 36-hour event)
            4. Location (provide a specific university building name and room number, not in JSON format, just plain text)
            5. Eligibility requirements (who can participate)
            6. Minimum rank required (choose from: Unranked, Bronze, Silver, Gold, Master, Grand Master, One Above All)
            7. Team size (between 2-4)
            8. Submission deadline (at the end of the 36-hour period)
            9. Tournament rules (detailed, including REQUIRED tech stack specifications - must include at least one frontend framework, one backend framework, and one database technology)
            10. Judging criteria (specific about technical complexity, code quality, innovation, scalability, and presentation)
            11. Project submission guidelines (code repository, demo video, API documentation)
            
            The hackathon should be significantly more challenging than a web design competition, requiring integration of multiple technologies.
            Format the response as JSON to be easily parsed.
            """
        else:  # Default to web_design or other types
            prompt = f"""
            Generate detailed information for a {tournament_type.replace('_', ' ')} tournament for university students based on the following description:
            {description}
            
            Please provide the following details in a structured format:
            1. Title (creative and engaging)
            2. Description (written from the POV of the company/organization with the problem - explain their situation, challenges, and what they hope students will create)
            3. Date and Time (a future date)
            4. Location (provide a specific university building name and room number, not in JSON format, just plain text)
            5. Eligibility requirements (who can participate)
            6. Minimum rank required (choose from: Unranked, Bronze, Silver, Gold, Master, Grand Master, One Above All)
            7. Team size (between 1-4)
            8. Submission deadline (before the tournament date)
            9. Tournament rules (detailed)
            10. Judging criteria (be specific based on the tournament type)
            11. Project submission guidelines (what needs to be submitted and how)
            
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
        
        # Ensure we have all the required fields and explicitly set the tournament type
        tournament_data["tournament_type"] = tournament_type
        return ensure_tournament_fields(tournament_data, tournament_type)
        
    except Exception as e:
        st.error(f"Error generating tournament: {e}")
        # Return default tournament data as fallback
        if tournament_type == "hackathon":
            default_data = generate_default_hackathon()
        else:
            default_data = generate_default_tournament()
        
        # Explicitly set the tournament type in the default data
        default_data["tournament_type"] = tournament_type
        return default_data
        
def generate_default_hackathon():
    """Generate default hackathon tournament data as fallback"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=30, hours=36)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "TechFusion Hackathon Challenge",
        "description": "At HealthTrack Solutions, we're facing a critical challenge: patients are struggling to adhere to their medication schedules, resulting in decreased treatment effectiveness. As a growing health tech provider, we need an innovative app solution that patients can use to track, be reminded of, and report on their medication usage. We're hosting this 36-hour hackathon to find teams who can build a user-friendly solution that integrates with our existing systems. The winning team will have the opportunity to continue development with our company.",
        "date_time": tournament_date,
        "location": "Innovation Hub, University Technology Center, Room 301",
        "eligibility": "Open to all university students with programming experience. Participants should have basic knowledge of web development technologies and database concepts.",
        "minimum_rank": "Silver",
        "team_size": 3,
        "deadline": submission_deadline,
        "rules": "1. All code must be original and created during the hackathon period.\n2. Teams must use the following technologies:\n   - Frontend: React.js or Vue.js\n   - Backend: Node.js (Express) or Python (Django/Flask)\n   - Database: MongoDB or PostgreSQL\n3. Use of third-party libraries and APIs is permitted but must be disclosed.\n4. Teams must commit code regularly to their repository.\n5. Applications must include authentication and at least one external API integration.\n6. Solutions must be responsive and work across different devices.\n7. Code must follow best practices for security and performance.",
        "judging_criteria": "1. Technical Complexity (25%): How sophisticated is the technical implementation?\n2. Innovation (20%): How original and creative is the solution?\n3. Functionality (20%): Does it work as intended with minimal bugs?\n4. Code Quality (15%): Is the code well-structured, documented, and maintainable?\n5. UI/UX Design (10%): Is the interface intuitive and visually appealing?\n6. Presentation (10%): How well did the team present their solution?",
        "project_submission": "Teams must submit:\n1. GitHub repository link with complete source code and documentation.\n2. A 3-minute demo video showcasing the application.\n3. API documentation if applicable.\n4. A README.md file explaining the solution, technologies used, and setup instructions.\n5. A presentation slide deck (maximum 10 slides)."
    }

def generate_default_tournament():
    """Generate default tournament data as fallback"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Creative Web Design Challenge",
        "description": "As the marketing director at WhiskerWonders, our cat café has been struggling with declining foot traffic. Our current website is outdated and fails to showcase the unique experience we offer to cat lovers. We need a fresh, engaging website that captures the cozy atmosphere of our café, highlights our rescue cats available for adoption, and makes our menu of cat-themed treats more appealing. We're looking for creative designers who can help us attract new customers and ultimately increase adoption rates for our rescue cats.",
        "date_time": tournament_date,
        "location": "Design School Auditorium, University Main Campus, Room 205",
        "eligibility": "Open to all university students with an interest in web design and development. Participants must be currently enrolled in an undergraduate or graduate program.",
        "minimum_rank": "Bronze",
        "team_size": 3,
        "deadline": submission_deadline,
        "rules": "1. All submissions must be original work.\n2. Designs must be responsive and work on mobile devices.\n3. Submissions must include at least 5 pages (home, about, our cats, menu, and contact).\n4. Teams must use HTML, CSS, and JavaScript for their implementation.\n5. Use of frameworks and libraries is permitted.\n6. Submissions must be accessible and follow WCAG guidelines.\n7. All assets used must be original or properly licensed.",
        "judging_criteria": "1. Visual Design (30%): Aesthetics, color scheme, typography, and overall visual appeal.\n2. User Experience (25%): Navigation, information architecture, and ease of use.\n3. Technical Implementation (20%): Code quality, performance, and proper implementation.\n4. Creativity (15%): Originality and innovative approach to the design challenge.\n5. Accessibility (10%): Compliance with accessibility standards.",
        "project_submission": "Teams must submit:\n1. A GitHub repository with all source code.\n2. A working URL where the website is deployed.\n3. A brief (500 words max) design document explaining the concept and implementation.\n4. A 3-minute video walkthrough of the website highlighting key features."
    }

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
        "project_submission": ["project submission", "submission guidelines"]
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

def ensure_tournament_fields(tournament_data, tournament_type="web_design"):
    """Ensure all required fields are present in tournament data"""
    if tournament_type == "hackathon":
        default_tournament = generate_default_hackathon()
    else:
        default_tournament = generate_default_tournament()
    
    # Explicitly set the tournament type
    tournament_data["tournament_type"] = tournament_type
    
    # Make sure all required fields exist
    for key in default_tournament:
        if key not in tournament_data or not tournament_data[key]:
            tournament_data[key] = default_tournament[key]
    
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
            # For hackathons, set deadline 36 hours after the start date
            if tournament_type == "hackathon":
                tournament_data["deadline"] = (datetime.now() + timedelta(days=30, hours=36)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                tournament_data["deadline"] = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["deadline"] = default_tournament["deadline"]
    
    return tournament_data

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
        "description": f"Our company, {topic['client'].split(',')[0]}, has been facing significant challenges with our online presence. {topic['description']} We're seeking talented student designers who can revolutionize our web presence with a focus on {topic['focus']}. The winning team will not only receive recognition but may have the opportunity to implement their design professionally.",
        "date_time": tournament_date,
        "location": "Digital Arts Building, University Design Lab, Room 302",
        "eligibility": "Open to all university students studying web design, computer science, graphic design, or related fields.",
        "minimum_rank": "Bronze",
        "team_size": 2,
        "deadline": submission_deadline,
        "rules": f"1. Create a complete responsive website focusing on {topic['focus']}.\n2. All code and design assets must be original or properly licensed.\n3. Website must include at least 5 main pages.\n4. Designs must be optimized for both desktop and mobile devices.\n5. Teams must use modern web technologies and follow best practices.",
        "judging_criteria": "1. Visual Design (30%): Brand alignment, aesthetics, and visual appeal.\n2. User Experience (25%): Intuitive navigation and overall usability.\n3. Technical Execution (20%): Code quality and performance.\n4. Creativity and Innovation (15%): Original ideas and unique approaches.\n5. Presentation (10%): How well the solution is presented and explained.",
        "project_submission": "Submit a GitHub repository link containing all code, a live demo URL, and a presentation PDF explaining your design choices.",
        "tournament_type": "web_design"
    }
    
def generate_creative_prompt(tournament_type):
    """Generate a creative prompt for tournament generation
    
    Args:
        tournament_type (str): Type of tournament to generate a prompt for
        
    Returns:
        str: A creative prompt
    """
    # Creative themes for different tournament types
    web_design_themes = [
        "Generate a creative web design tournament about a luxury pet hotel needing a website to showcase their premium services and attract high-end clientele.",
        "Generate a creative web design tournament about a virtual reality arcade trying to build an immersive website that reflects their futuristic gaming experiences.",
        "Generate a creative web design tournament about a sustainable fashion brand needing a website that highlights their eco-friendly practices and unique designs.",
        "Generate a creative web design tournament about a historic bookstore with rare collections needing a website that balances classic aesthetics with modern functionality.",
        "Generate a creative web design tournament about a food delivery service specialized in international cuisines needing a website to showcase global flavors.",
        "Generate a creative web design tournament about a space tourism company needing a website to attract adventurous travelers for their upcoming orbital flights.",
        "Generate a creative web design tournament about a music festival needing a dynamic website to promote their lineup of artists and sell tickets.",
        "Generate a creative web design tournament about an underwater photography gallery needing a website that captures the beauty of marine life.",
        "Generate a creative web design tournament about a smart home technology company needing a website that demonstrates their innovative products.",
        "Generate a creative web design tournament about a community garden organization needing a website to attract volunteers and share gardening resources."
    ]
    
    hackathon_themes = [
        "Generate a 36-hour hackathon focused on creating solutions for disaster response and emergency management systems.",
        "Generate a 36-hour hackathon focused on developing educational technology for children with learning disabilities.",
        "Generate a 36-hour hackathon focused on creating financial technology solutions for underbanked communities.",
        "Generate a 36-hour hackathon focused on building sustainable smart city infrastructure and monitoring systems.",
        "Generate a 36-hour hackathon focused on developing mental health support applications and resources.",
        "Generate a 36-hour hackathon focused on creating accessibility tools for people with disabilities.",
        "Generate a 36-hour hackathon focused on developing AI-powered agriculture solutions for small farms.",
        "Generate a 36-hour hackathon focused on creating privacy-focused alternatives to mainstream tech products.",
        "Generate a 36-hour hackathon focused on developing telehealth solutions for rural communities.",
        "Generate a 36-hour hackathon focused on creating augmented reality applications for industrial training."
    ]
    
    mobile_themes = [
        "Generate a mobile app development competition focused on health monitoring and wellness tracking.",
        "Generate a mobile app development competition focused on location-based augmented reality games.",
        "Generate a mobile app development competition focused on personal finance management and financial literacy.",
        "Generate a mobile app development competition focused on language learning and cultural exchange.",
        "Generate a mobile app development competition focused on community volunteering and social impact.",
        "Generate a mobile app development competition focused on sustainable living and carbon footprint reduction.",
        "Generate a mobile app development competition focused on collaborative music creation and sharing.",
        "Generate a mobile app development competition focused on mental health support and mindfulness.",
        "Generate a mobile app development competition focused on accessible navigation for people with disabilities.",
        "Generate a mobile app development competition focused on local tourism and hidden gem discovery."
    ]
    
    coding_themes = [
        "Generate a competitive programming contest focused on algorithm optimization for renewable energy systems.",
        "Generate a competitive programming contest focused on machine learning challenges for medical diagnosis.",
        "Generate a competitive programming contest focused on natural language processing for multilingual communication.",
        "Generate a competitive programming contest focused on computer vision for wildlife conservation.",
        "Generate a competitive programming contest focused on blockchain solutions for supply chain transparency.",
        "Generate a competitive programming contest focused on quantum computing algorithm simulation.",
        "Generate a competitive programming contest focused on cybersecurity challenges and ethical hacking.",
        "Generate a competitive programming contest focused on data analysis for climate change research.",
        "Generate a competitive programming contest focused on game AI development and strategy optimization.",
        "Generate a competitive programming contest focused on robotics control systems and automation."
    ]
    
    # Select themes based on tournament type
    if tournament_type == "web_design":
        themes = web_design_themes
    elif tournament_type == "hackathon":
        themes = hackathon_themes
    elif tournament_type == "mobile":
        themes = mobile_themes
    elif tournament_type == "coding_competition":
        themes = coding_themes
    else:
        # For other types, use a mix of themes
        import random
        themes = random.sample(web_design_themes, 3) + random.sample(hackathon_themes, 3) + random.sample(mobile_themes, 2)
    
    # Return a random theme
    import random
    return random.choice(themes)