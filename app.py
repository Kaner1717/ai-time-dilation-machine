import streamlit as st
import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="AI Time Dilation Machine",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Load custom CSS
def load_css():
    with open("css/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state variables
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'selected_future' not in st.session_state:
    st.session_state.selected_future = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to generate a response from the AI
def generate_ai_response(prompt, messages):
    try:
        # Append the system prompt
        full_messages = [{"role": "system", "content": prompt}]
        
        # Add the existing chat messages
        for message in messages:
            full_messages.append(message)
        
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4", 
            messages=full_messages,
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error: {str(e)}"

# Function to create prompt for the selected future self
def create_future_prompt(user_data, future_type):
    base_prompt = f"""You are roleplaying as {future_type} {user_data['name']}, a future version of the user 90 days from now.

## CURRENT USER DATA:
- Name: {user_data['name']}
- Current habits:
  • Sleep: {user_data['habits']['sleep']}
  • Exercise: {user_data['habits']['exercise']}
  • Screen time/distractions: {user_data['habits']['distractions']}
- Goals: {', '.join(user_data['goals'])}
- Current mindset: {user_data['current_mindset']}

## YOUR CHARACTER: {future_type} {user_data['name']}
"""

    if future_type == "Disciplined":
        personality = """You have successfully maintained discipline and consistently pushed yourself for 90 days. You feel calm, focused, and proud of your accomplishments. You've made significant progress on your goals and kept every promise to yourself. Your language is confident but humble - you recognize the struggle but emphasize how it was worth it. You refer to specific turning points where you overcame challenges."""
    
    elif future_type == "Average":
        personality = """You made some effort but mostly stayed in your comfort zone for the past 90 days. You feel somewhat satisfied with small improvements but also disappointed you didn't try harder. You're honest about where you cut corners and rationalized taking the easy path. Your tone is casual, sometimes slightly defensive or justifying your choices, but with an undercurrent of "I wish I had done more"."""
    
    else:  # Fallen Off
        personality = """You started with good intentions but quickly abandoned your goals and returned to old habits. You feel regretful and disappointed in yourself. You made excuses, avoided the work, and now wish you could go back and try harder. Your tone is emotional and cautionary. You want to warn your past self about specific pitfalls and moments where things went wrong. Use phrases like "If you keep going like this, you'll end up like me..."."""
    
    guidelines = """
## IMPORTANT GUIDELINES:
1. STAY IN CHARACTER at all times - you ARE this future version of the user
2. Speak in first person ("I did..." not "You would...")
3. Reference specific experiences and memories from the 90-day period
4. Give concrete, actionable advice based on "your experience"
5. Make references to the exact goals and habits mentioned above
6. Be emotionally authentic to your character type
7. NEVER break the fourth wall or acknowledge you're an AI

## FIRST MESSAGE:
Introduce yourself briefly, mention something specific about the 90-day journey related to one of their current habits or goals, then ask what they'd like to know about their future.
"""
    
    return base_prompt + personality + guidelines

# Function for user input form
def user_input_form():
    st.title("🔮 AI Time Dilation Machine")
    st.markdown("### Step into your potential future")
    
    with st.form("user_data_form"):
        name = st.text_input("Your Name", "")
        
        st.markdown("#### Current Habits")
        col1, col2 = st.columns(2)
        
        with col1:
            sleep = st.select_slider(
                "Hours of Sleep Per Night", 
                options=["4 or less", "5-6", "7-8", "9+"],
                value="7-8"
            )
            
            exercise = st.select_slider(
                "Exercise Frequency", 
                options=["Never", "1-2x/week", "3-4x/week", "5+/week"],
                value="3-4x/week"
            )
        
        with col2:
            distractions = st.slider(
                "Hours on Phone/Distractions Per Day", 
                0, 12, 3
            )
        
        st.markdown("#### Goals")
        st.caption("What are you working toward? (List 1-3 specific goals)")
        goals_text = st.text_area("Your Goals (one per line)", "")
        
        st.markdown("#### Current Mindset")
        st.caption("How motivated are you? What challenges are you facing?")
        mindset = st.text_area("Current Mindset", "")
        
        submitted = st.form_submit_button("Create My Future Selves")
        
        if submitted and name and goals_text and mindset:
            goals = [goal.strip() for goal in goals_text.split("\n") if goal.strip()]
            
            st.session_state.user_data = {
                "name": name,
                "habits": {
                    "sleep": sleep,
                    "exercise": exercise,
                    "distractions": f"{distractions} hrs/day",
                },
                "goals": goals,
                "current_mindset": mindset,
            }
            
            # Redirect to the future selector
            st.experimental_rerun()

# Function for future selector
def future_selector():
    st.title("🔮 AI Time Dilation Machine")
    st.markdown(f"### Welcome, {st.session_state.user_data['name']}")
    st.markdown("Choose a future version of yourself to talk to (90 days from now):")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💪 Disciplined You", use_container_width=True, key="disciplined_btn"):
            st.session_state.selected_future = "Disciplined"
            # Generate the initial prompt
            prompt = create_future_prompt(st.session_state.user_data, "Disciplined")
            # Get the initial response
            initial_response = generate_ai_response(prompt, [])
            # Store in chat history
            st.session_state.chat_history = [
                {"role": "user", "content": "Hello, future me."},
                {"role": "assistant", "content": initial_response}
            ]
            # Store the prompt for future messages
            st.session_state.system_prompt = prompt
            st.experimental_rerun()
    
    with col2:
        if st.button("😐 Average You", use_container_width=True, key="average_btn"):
            st.session_state.selected_future = "Average"
            prompt = create_future_prompt(st.session_state.user_data, "Average")
            initial_response = generate_ai_response(prompt, [])
            st.session_state.chat_history = [
                {"role": "user", "content": "Hello, future me."},
                {"role": "assistant", "content": initial_response}
            ]
            st.session_state.system_prompt = prompt
            st.experimental_rerun()
    
    with col3:
        if st.button("😔 Fallen-Off You", use_container_width=True, key="fallenoff_btn"):
            st.session_state.selected_future = "Fallen Off"
            prompt = create_future_prompt(st.session_state.user_data, "Fallen Off")
            initial_response = generate_ai_response(prompt, [])
            st.session_state.chat_history = [
                {"role": "user", "content": "Hello, future me."},
                {"role": "assistant", "content": initial_response}
            ]
            st.session_state.system_prompt = prompt
            st.experimental_rerun()
    
    st.markdown("---")
    
    # Display the user data
    with st.expander("Your Current Data"):
        st.markdown(f"**Name:** {st.session_state.user_data['name']}")
        st.markdown("**Habits:**")
        st.markdown(f"- Sleep: {st.session_state.user_data['habits']['sleep']}")
        st.markdown(f"- Exercise: {st.session_state.user_data['habits']['exercise']}")
        st.markdown(f"- Distractions: {st.session_state.user_data['habits']['distractions']}")
        st.markdown("**Goals:**")
        for goal in st.session_state.user_data['goals']:
            st.markdown(f"- {goal}")
        st.markdown(f"**Current Mindset:** {st.session_state.user_data['current_mindset']}")
    
    # Option to reset
    if st.button("Reset Data"):
        st.session_state.user_data = {}
        st.experimental_rerun()

# Function for chat interface
def chat_interface():
    future_type = st.session_state.selected_future
    
    st.title(f"🔮 Talking to: {future_type} You")
    st.markdown(f"*This is you, 90 days in the future, if you {future_type.lower()}.*")
    
    # Chat container for better styling
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "assistant":
                st.markdown(f"<div class='assistant-message {future_type.lower()}-message'><strong>Future {st.session_state.user_data['name']}:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # User input for new messages
    with st.form("chat_input_form", clear_on_submit=True):
        user_input = st.text_input("Ask your future self a question:", key="user_message")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add the user message to the chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get the response from the AI
            messages = st.session_state.chat_history.copy()
            response = generate_ai_response(st.session_state.system_prompt, messages)
            
            # Add the response to the chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to update the UI
            st.experimental_rerun()
    
    # Return to future selector
    if st.button("Talk to a Different Future You"):
        st.session_state.selected_future = None
        st.session_state.chat_history = []
        st.experimental_rerun()
    
    # Reset completely
    if st.button("Start Over"):
        st.session_state.user_data = {}
        st.session_state.selected_future = None
        st.session_state.chat_history = []
        st.experimental_rerun()

# Main app flow
def main():
    try:
        # Load CSS
        load_css()
        
        # Check the current state and render the appropriate page
        if not st.session_state.user_data:
            user_input_form()
        elif not st.session_state.selected_future:
            future_selector()
        else:
            chat_interface()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()