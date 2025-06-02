import openai
import streamlit as st
from datetime import datetime, timedelta
import random
import json

def generate_tournament_with_openai(description="", tournament_type="web_design"):
    """Generate tournament details using OpenAI GPT-3.5 Turbo
    
    Args:
        description (str): User description for the tournament (can be default or custom)
        tournament_type (str): Type of tournament (web_design, hackathon, etc.)
        
    Returns:
        dict: Tournament details
    """
    try:
        # Use the provided description (whether it's default or custom)
        # Add Bloom's Taxonomy 'Create' level emphasis
        create_level_context = """
        This tournament should align with the 'Create' level of Bloom's Taxonomy. 
        The tasks should focus on designing, building, constructing, planning, producing, 
        inventing, devising, making, and composing new and original solutions. 
        Use action verbs like: create, design, develop, formulate, build, construct, produce, invent, devise, 
        make, generate, compose, originate, plan, and synthesize in task descriptions.
        """
        
        # Build prompt based on tournament type with the exact description provided
        if tournament_type == "hackathon":
            prompt = f"""
            Generate detailed information for a hackathon tournament for university students based on the following description:
            {description}
            
            {create_level_context}
            
            Please provide the following details in a structured JSON format:
            {{
                "title": "creative and engaging, technical-sounding title",
                "description": "written from the POV of the company/organization with the problem - explain their situation, challenges, and what they hope students will create. MUST be based on: {description}",
                "date_time": "future date, specifically a 36-hour event (YYYY-MM-DD HH:MM:SS format)",
                "location": "specific university building name and room number",
                "eligibility": "who can participate",
                "minimum_rank": "choose from: Unranked, Bronze, Silver, Gold, Master, Grand Master, One Above All",
                "team_size": "number between 2-4",
                "deadline": "at the end of the 36-hour period (YYYY-MM-DD HH:MM:SS format)",
                "rules": "detailed, including REQUIRED tech stack specifications - must include at least one frontend framework, one backend framework, and one database technology",
                "project_submission": "code repository, demo video, API documentation requirements"
            }}
            
            IMPORTANT: The tournament must be directly based on this description: {description}
            DO NOT generate judging criteria - this will be handled separately based on rubrics.
            The hackathon should challenge students to create, construct, and design innovative solutions that are original and new.
            """
        else:  # All other tournament types
            prompt = f"""
            Generate detailed information for a {tournament_type.replace('_', ' ')} tournament for university students based on the following description:
            {description}
            
            {create_level_context}
            
            Please provide the following details in a structured JSON format:
            {{
                "title": "creative and engaging title",
                "description": "written from the POV of the company/organization with the problem - explain their situation, challenges, and what they hope students will create. MUST be based on: {description}",
                "date_time": "future date (YYYY-MM-DD HH:MM:SS format)",
                "location": "specific university building name and room number",
                "eligibility": "who can participate",
                "minimum_rank": "choose from: Unranked, Bronze, Silver, Gold, Master, Grand Master, One Above All",
                "team_size": "number between 1-4",
                "deadline": "before the tournament date (YYYY-MM-DD HH:MM:SS format)",
                "rules": "detailed rules for the tournament",
                "project_submission": "what needs to be submitted and how"
            }}
            
            IMPORTANT: The tournament must be directly based on this description: {description}
            DO NOT generate judging criteria - this will be handled separately based on rubrics.
            Be creative with the theme and make it engaging for university students. The title should be catchy and related to the theme.
            Emphasize creative, innovative, and original solutions - students should be designing and producing new and original work.
            """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a tournament planning assistant that creates detailed creative competitions for university students. Your tournaments emphasize the 'Create' level of Bloom's Taxonomy, focusing on design, building, and producing original solutions. CRITICAL: You must base the tournament on this exact description: {description}. Do not generate judging criteria as this will be handled by rubrics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
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
        
        # Verify that AI actually used the description, if not create custom tournament
        if not verify_ai_used_description(tournament_data, description):
            st.warning("AI didn't fully incorporate your description. Creating a custom tournament based on your prompt.")
            tournament_data = create_tournament_from_description(description, tournament_type)
        
        # IMPORTANT: Set empty judging criteria - it will be populated by rubrics
        tournament_data["judging_criteria"] = ""
        
        # Ensure we have all the required fields and explicitly set the tournament type
        tournament_data["tournament_type"] = tournament_type
        return ensure_tournament_fields(tournament_data, tournament_type)
        
    except Exception as e:
        st.error(f"Error generating tournament with AI: {e}")
        st.info("Creating a tournament based on your description instead.")
        
        # Create tournament based on the actual description provided (not defaults)
        return create_tournament_from_description(description, tournament_type)

def verify_ai_used_description(tournament_data, description):
    """Verify that the AI actually incorporated the user's description"""
    if not description or len(description.strip()) < 10:
        return True  # Can't verify short descriptions
    
    generated_desc = tournament_data.get("description", "").lower()
    desc_lower = description.lower()
    
    # Extract meaningful keywords from user description
    common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "about", "into", "through", "during", "before", "after", "above", "below", "up", "down", "out", "off", "over", "under", "again", "further", "then", "once", "that", "this", "these", "those", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "need", "needs", "want", "wants"}
    
    user_keywords = set(desc_lower.split()) - common_words
    
    # Check if any meaningful keywords from user description appear in generated description
    matches = sum(1 for keyword in user_keywords if len(keyword) > 3 and keyword in generated_desc)
    
    # If we have meaningful keywords but none appear in the generated description, AI probably didn't use it
    if len(user_keywords) > 2 and matches == 0:
        return False
    
    return True

def create_tournament_from_description(description, tournament_type):
    """Create a tournament based on user description when AI fails or doesn't use the prompt"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=26)).strftime("%Y-%m-%d %H:%M:%S")
    
    # For hackathons, adjust timing
    if tournament_type == "hackathon":
        submission_deadline = (datetime.now() + timedelta(days=30, hours=36)).strftime("%Y-%m-%d %H:%M:%S")
        judging_date = (datetime.now() + timedelta(days=31, hours=12)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract meaningful context from description
    desc_lower = description.lower()
    
    # Determine client, focus, and title based on keywords in description
    if "zoo" in desc_lower:
        client = "Metro City Zoo"
        focus = "wildlife showcases and visitor engagement"
        title = "Zoo Digital Experience Challenge"
        specific_rules = "Solutions must include animal profiles, interactive maps, and visitor planning tools."
    elif "hospital" in desc_lower or "medical" in desc_lower or "healthcare" in desc_lower:
        client = "Regional Medical Center"
        focus = "patient care and medical accessibility"
        title = "Healthcare Digital Innovation Challenge"
        specific_rules = "Solutions must prioritize patient privacy, accessibility, and medical information clarity."
    elif "school" in desc_lower or "education" in desc_lower or "university" in desc_lower:
        client = "Springfield Educational District"
        focus = "student learning and educational engagement"
        title = "Educational Technology Challenge"
        specific_rules = "Solutions must support different learning styles and educational accessibility."
    elif "restaurant" in desc_lower or "food" in desc_lower or "cafe" in desc_lower or "café" in desc_lower:
        client = "Local Restaurant Collective"
        focus = "dining experience and customer engagement"
        title = "Culinary Digital Experience Challenge"
        specific_rules = "Solutions must include menu displays, ordering systems, and customer experience features."
    elif "museum" in desc_lower or "gallery" in desc_lower:
        client = "City Museum"
        focus = "cultural preservation and virtual exhibitions"
        title = "Museum Digital Experience Challenge"
        specific_rules = "Solutions must include virtual tours, artifact showcases, and educational content."
    elif "shop" in desc_lower or "store" in desc_lower or "ecommerce" in desc_lower or "e-commerce" in desc_lower:
        client = "Local Business Collective"
        focus = "online shopping and customer experience"
        title = "E-Commerce Innovation Challenge"
        specific_rules = "Solutions must include product catalogs, shopping carts, and secure payment integration."
    elif "library" in desc_lower:
        client = "City Library System"
        focus = "digital resources and community engagement"
        title = "Library Digital Services Challenge"
        specific_rules = "Solutions must include book catalogs, reservation systems, and community features."
    elif "bank" in desc_lower or "financial" in desc_lower:
        client = "Community Bank"
        focus = "financial services and customer security"
        title = "Financial Services Digital Challenge"
        specific_rules = "Solutions must prioritize security, user authentication, and financial data protection."
    elif "travel" in desc_lower or "tourism" in desc_lower:
        client = "Tourism Board"
        focus = "destination promotion and trip planning"
        title = "Travel Experience Digital Challenge"
        specific_rules = "Solutions must include destination guides, booking systems, and travel planning tools."
    elif "fitness" in desc_lower or "gym" in desc_lower or "sports" in desc_lower:
        client = "Community Fitness Center"
        focus = "health tracking and workout planning"
        title = "Fitness Technology Challenge"
        specific_rules = "Solutions must include workout tracking, progress monitoring, and community features."
    else:
        # Generic but descriptive fallback
        client = "Community Organization"
        focus = "user experience and digital innovation"
        title = f"{tournament_type.replace('_', ' ').title()} Innovation Challenge"
        specific_rules = "Solutions must address the specific needs outlined in the challenge description."
    
    # Create tournament type-specific rules
    base_rules = f"1. All solutions must directly address this challenge: {description}\n2. Submissions must be original work created during the tournament period.\n3. {specific_rules}\n4. Teams must present their solutions to a panel of judges."
    
    if tournament_type == "hackathon":
        base_rules += "\n5. Required tech stack: Frontend framework (React/Vue/Angular), Backend framework (Node.js/Python/Java), Database (MongoDB/PostgreSQL/MySQL)\n6. Solutions must include API documentation and deployment instructions.\n7. Code must be committed regularly to version control."
    elif tournament_type == "web_design":
        base_rules += "\n5. Designs must be responsive and work on mobile devices.\n6. Must follow web accessibility guidelines (WCAG).\n7. Use modern web technologies and frameworks."
    elif tournament_type == "mobile":
        base_rules += "\n5. Applications must work on both iOS and Android platforms.\n6. Must include offline functionality where appropriate.\n7. Focus on mobile-first design principles."
    elif tournament_type == "coding_competition":
        base_rules += "\n5. Solutions must demonstrate algorithmic efficiency.\n6. Code must be well-documented and maintainable.\n7. Include comprehensive testing and performance analysis."
    elif tournament_type == "coup_detat":
        base_rules += "\n5. Strategic gameplay must be balanced and engaging.\n6. Include comprehensive rule documentation.\n7. Solutions should support multiple players and game sessions."
    
    return {
        "title": title,
        "description": f"Challenge: {description}\n\nOur organization, {client}, is facing the challenges described above. We need innovative solutions that focus on {focus}. This tournament challenges students to create, design, and build original solutions that directly address these specific needs. Your solution should demonstrate creativity, technical excellence, and practical applicability to real-world problems. We're looking for teams who can think outside the box and deliver professional-quality results.",
        "date_time": tournament_date,
        "location": "Innovation Hub, University Technology Center, Room 301",
        "eligibility": "Open to all university students with relevant technical skills and creative problem-solving abilities. Participants should have experience with modern development technologies and user experience design principles.",
        "minimum_rank": "Bronze",
        "team_size": 3 if tournament_type == "hackathon" else 2,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": base_rules,
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": get_project_submission_requirements(tournament_type),
        "tournament_type": tournament_type
    }

def get_project_submission_requirements(tournament_type):
    """Get tournament type-specific submission requirements"""
    base_requirements = "Teams must submit: 1) Complete source code repository with clear documentation"
    
    if tournament_type == "hackathon":
        return base_requirements + ", 2) Working demo with live deployment, 3) API documentation and technical architecture, 4) 5-minute video demonstration, 5) Presentation slides highlighting innovation and technical approach."
    elif tournament_type == "web_design":
        return base_requirements + ", 2) Live website deployment with working functionality, 3) Design documentation explaining user experience decisions, 4) Responsive design demonstration across devices, 5) Brief presentation (5-10 minutes) showcasing design process."
    elif tournament_type == "mobile":
        return base_requirements + ", 2) Working mobile application (APK/IPA files), 3) App demonstration video showing all features, 4) User interface design documentation, 5) Presentation explaining mobile-specific design decisions."
    elif tournament_type == "coding_competition":
        return base_requirements + ", 2) Algorithm analysis and performance documentation, 3) Comprehensive test cases and results, 4) Code complexity analysis, 5) Technical presentation explaining solution approach."
    elif tournament_type == "coup_detat":
        return base_requirements + ", 2) Complete game implementation with working mechanics, 3) Game rules documentation and player guide, 4) Demonstration of gameplay scenarios, 5) Strategic analysis presentation."
    else:
        return base_requirements + ", 2) Working demonstration of the solution, 3) Technical documentation explaining implementation, 4) User experience documentation, 5) Presentation highlighting key innovations."

def generate_default_hackathon():
    """Generate default hackathon tournament data as fallback"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=30, hours=36)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=31, hours=12)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "TechFusion Hackathon Challenge",
        "description": "At HealthTrack Solutions, we're facing a critical challenge: patients are struggling to adhere to their medication schedules, resulting in decreased treatment effectiveness. As a growing health tech provider, we need an innovative app solution that patients can use to track, be reminded of, and report on their medication usage. We're hosting this 36-hour hackathon to find teams who can build a user-friendly solution that integrates with our existing systems. The winning team will have the opportunity to continue development with our company.",
        "date_time": tournament_date,
        "location": "Innovation Hub, University Technology Center, Room 301",
        "eligibility": "Open to all university students with programming experience. Participants should have basic knowledge of web development technologies and database concepts.",
        "minimum_rank": "Silver",
        "team_size": 3,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": "1. All code must be original and created during the hackathon period.\n2. Teams must use the following technologies:\n   - Frontend: React.js or Vue.js\n   - Backend: Node.js (Express) or Python (Django/Flask)\n   - Database: MongoDB or PostgreSQL\n3. Use of third-party libraries and APIs is permitted but must be disclosed.\n4. Teams must commit code regularly to their repository.\n5. Applications must include authentication and at least one external API integration.\n6. Solutions must be responsive and work across different devices.\n7. Code must follow best practices for security and performance.",
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": "Teams must submit:\n1. GitHub repository link with complete source code and documentation.\n2. A 3-minute demo video showcasing the application.\n3. API documentation if applicable.\n4. A README.md file explaining the solution, technologies used, and setup instructions.\n5. A presentation slide deck (maximum 10 slides)."
    }

def generate_default_tournament():
    """Generate default web design tournament data as fallback"""
    tournament_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=26)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Creative Web Design Challenge",
        "description": "As the marketing director at WhiskerWonders, our cat café has been struggling with declining foot traffic. Our current website is outdated and fails to showcase the unique experience we offer to cat lovers. We need a fresh, engaging website that captures the cozy atmosphere of our café, highlights our rescue cats available for adoption, and makes our menu of cat-themed treats more appealing. We're looking for creative designers who can help us attract new customers and ultimately increase adoption rates for our rescue cats.",
        "date_time": tournament_date,
        "location": "Design School Auditorium, University Main Campus, Room 205",
        "eligibility": "Open to all university students with an interest in web design and development. Participants must be currently enrolled in an undergraduate or graduate program.",
        "minimum_rank": "Bronze",
        "team_size": 3,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": "1. All submissions must be original work.\n2. Designs must be responsive and work on mobile devices.\n3. Submissions must include at least 5 pages (home, about, our cats, menu, and contact).\n4. Teams must use HTML, CSS, and JavaScript for their implementation.\n5. Use of frameworks and libraries is permitted.\n6. Submissions must be accessible and follow WCAG guidelines.\n7. All assets used must be original or properly licensed.",
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": "Teams must submit:\n1. A GitHub repository with all source code.\n2. A working URL where the website is deployed.\n3. A brief (500 words max) design document explaining the concept and implementation.\n4. A 3-minute video walkthrough of the website highlighting key features."
    }

def generate_default_coup_detat():
    """Generate default coup d'état tournament data"""
    tournament_date = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Digital Democracy Strategic Challenge",
        "description": "The fictional nation of Strategia is facing political instability, and various factions are vying for control. As strategic consultants, your team must design and implement a digital platform that simulates political maneuvering, alliance building, and resource management. This tournament challenges you to create an engaging strategy game that demonstrates understanding of political dynamics, game theory, and user engagement. Your solution should be both educational and entertaining, allowing players to experience the complexities of political strategy.",
        "date_time": tournament_date,
        "location": "Strategy Lab, University Business School, Room 401",
        "eligibility": "Open to university students with interest in strategy games, political science, or game development. Teams should have programming skills and understanding of strategic gameplay.",
        "minimum_rank": "Silver",
        "team_size": 4,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": "1. Create a digital strategy game with political themes.\n2. Game must support multiple players and strategic decision-making.\n3. Include comprehensive rule documentation and player guides.\n4. Implement balanced gameplay mechanics.\n5. All code and assets must be original.\n6. Game should be educational while remaining engaging.\n7. Include multiplayer functionality or AI opponents.",
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": "Teams must submit:\n1. Complete game implementation with source code.\n2. Comprehensive game rules and strategy guide.\n3. Demonstration video showing gameplay scenarios.\n4. Technical documentation explaining game architecture.\n5. Presentation analyzing strategic elements and design decisions."
    }

def generate_default_coding_competition():
    """Generate default coding competition tournament data"""
    tournament_date = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=27)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Algorithm Mastery Championship",
        "description": "TechCorp Industries processes massive datasets daily and needs optimized algorithms for various computational challenges. From sorting millions of records to finding optimal paths through complex networks, we face algorithmic problems that require both theoretical knowledge and practical implementation skills. This competition challenges participants to solve real-world computational problems while demonstrating mastery of data structures, algorithm design, and performance optimization. Winners will have opportunities for internships and full-time positions.",
        "date_time": tournament_date,
        "location": "Computer Science Building, Advanced Computing Lab, Room 501",
        "eligibility": "Open to university students with strong programming backgrounds. Participants should be proficient in at least one programming language and familiar with data structures and algorithms.",
        "minimum_rank": "Gold",
        "team_size": 2,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": "1. Solve a series of algorithmic challenges within time limits.\n2. Solutions must be original and implemented during the competition.\n3. Code must be well-documented and efficient.\n4. Multiple programming languages allowed (Python, Java, C++, etc.).\n5. Include time and space complexity analysis.\n6. Provide comprehensive test cases.\n7. Focus on both correctness and performance optimization.",
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": "Teams must submit:\n1. Source code for all solutions with documentation.\n2. Algorithm analysis explaining time/space complexity.\n3. Comprehensive test cases and performance benchmarks.\n4. Technical report explaining problem-solving strategies.\n5. Presentation demonstrating key algorithmic insights."
    }

def generate_default_mobile():
    """Generate default mobile tournament data"""
    tournament_date = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d %H:%M:%S")
    submission_deadline = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S")
    judging_date = (datetime.now() + timedelta(days=29)).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": "Mobile Innovation Challenge",
        "description": "EduConnect is an educational technology startup struggling to engage students in remote learning environments. Traditional desktop solutions don't work for students who primarily use mobile devices for learning. We need innovative mobile applications that make learning interactive, accessible, and engaging for students of all ages. The app should work offline, support multiple learning styles, and provide progress tracking for both students and educators. This challenge focuses on creating mobile-first educational experiences.",
        "date_time": tournament_date,
        "location": "Mobile Development Lab, University Tech Center, Room 201",
        "eligibility": "Open to university students with mobile development experience. Participants should be familiar with iOS, Android, or cross-platform development frameworks.",
        "minimum_rank": "Bronze",
        "team_size": 3,
        "deadline": submission_deadline,
        "judging_date": judging_date,
        "rules": "1. Develop a mobile application for iOS and/or Android.\n2. App must work offline and sync when connected.\n3. Focus on mobile-first design principles.\n4. Include user authentication and data persistence.\n5. Ensure accessibility compliance for mobile devices.\n6. Test on multiple device sizes and orientations.\n7. All code and assets must be original work.",
        "judging_criteria": "",  # Empty - will be populated by rubrics
        "project_submission": "Teams must submit:\n1. Complete mobile application (APK/IPA files).\n2. Source code repository with build instructions.\n3. App demonstration video showing all features.\n4. Technical documentation explaining mobile-specific decisions.\n5. Presentation highlighting user experience design process."
    }

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
    # Get the appropriate default based on tournament type
    if tournament_type == "hackathon":
        default_tournament = generate_default_hackathon()
    elif tournament_type == "coup_detat":
        default_tournament = generate_default_coup_detat()
    elif tournament_type == "coding_competition":
        default_tournament = generate_default_coding_competition()
    elif tournament_type == "mobile":
        default_tournament = generate_default_mobile()
    else:  # web_design and others
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
            datetime.strptime(tournament_data["date_time"], "%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["date_time"] = default_tournament["date_time"]
    
    if isinstance(tournament_data["deadline"], str):
        try:
            # Try to parse the deadline
            datetime.strptime(tournament_data["deadline"], "%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["deadline"] = default_tournament["deadline"]
    
    # Set judging date to one day after the deadline if not provided
    if "judging_date" not in tournament_data or not tournament_data["judging_date"]:
        try:
            deadline_date = datetime.strptime(tournament_data["deadline"], "%Y-%m-%d %H:%M:%S")
            tournament_data["judging_date"] = (deadline_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            tournament_data["judging_date"] = default_tournament.get("judging_date", (datetime.now() + timedelta(days=26)).strftime("%Y-%m-%d %H:%M:%S"))
    
    return tournament_data

def generate_creative_web_topics(count=3):
    """
    Generate creative web design tournament topics using GPT-3.5
    
    Args:
        count (int): Number of topics to generate
        
    Returns:
        list: List of topic dictionaries with title and description
    """
    try:
        # Add Bloom's Taxonomy 'Create' level emphasis
        create_level_context = """
        These topics should align with the 'Create' level of Bloom's Taxonomy.
        Focus on tasks that involve designing, building, constructing, planning, 
        producing, inventing, devising, and composing new and original solutions.
        """
        
        prompt = f"""
        Generate {count} creative and unique web design tournament topics for university students.
        Each topic should have a different focus and theme.
        
        {create_level_context}
        
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
                {"role": "system", "content": "You are a creative director specializing in web design competitions that challenge students to create original and innovative designs."},
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
        "judging_criteria": "",  # Empty - will be populated by rubrics
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
    
    coup_detat_themes = [
        "Generate a strategic coup d'état tournament focused on medieval kingdom political maneuvering and alliance building.",
        "Generate a strategic coup d'état tournament focused on corporate takeover scenarios and business strategy.",
        "Generate a strategic coup d'état tournament focused on space colony governance and resource management.",
        "Generate a strategic coup d'état tournament focused on revolutionary movements and resistance strategies.",
        "Generate a strategic coup d'état tournament focused on diplomatic negotiations in a fractured empire.",
        "Generate a strategic coup d'état tournament focused on cyberpunk corporate espionage and digital warfare.",
        "Generate a strategic coup d'état tournament focused on post-apocalyptic faction control and survival.",
        "Generate a strategic coup d'état tournament focused on fantasy realm political intrigue and magic.",
        "Generate a strategic coup d'état tournament focused on historical revolution simulation and strategy.",
        "Generate a strategic coup d'état tournament focused on interstellar federation politics and alien diplomacy."
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
    elif tournament_type == "coup_detat":
        themes = coup_detat_themes
    else:
        # For other types, use a mix of themes
        themes = random.sample(web_design_themes, 3) + random.sample(hackathon_themes, 3) + random.sample(mobile_themes, 2)
    
    # Return a random theme
    return random.choice(themes)