import streamlit as st
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration & SEO
st.set_page_config(
    page_title="Reasonable AI - Autonomous Reasoning Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/HassanRJ-3108/Reasonable-AI/issues',
        'Report a bug': 'https://github.com/HassanRJ-3108/Reasonable-AI/issues/new',
        'About': """
        # Reasonable AI
        
        An autonomous reasoning chatbot powered by Google's Gemini models.
        
        Created by Hassan RJ, Full Stack Web Developer and GIAIC Student Leader.
        
        Version: 1.0.0
        """
    }
)
st.markdown("""
    <head>
        <meta name="description" content="Learn AI concepts in a simple and understandable way with Reasonable AI. Perfect for beginners and developers. Explore clear explanations, examples, and tutorials.">
    </head>
    """, unsafe_allow_html=True)
# Custom CSS for styling
st.markdown("""
<style>
    /* Improved overall styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Improved sections */
    .settings-section {
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #ddd;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 12px;
    }
    
    /* Improved header styling */
    h1, h2, h3 {
        font-weight: 600;
    }
    
    /* Improved expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #495057;
    }
    
    /* Improved button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        padding: 6px 16px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Application title and creator info
st.title("🧠 Reasonable AI")
st.markdown("An autonomous reasoning chatbot by Hassan RJ")

# Creator information
st.markdown("""
**Created by Hassan RJ**
- Full Stack Web Developer
- Student Leader at GIAIC
- Currently learning modern-ai-python
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key section
    st.subheader("API Key")
    # Try to get API key from environment variable first
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    # If not found in environment, ask user to input
    if not api_key:
        api_key = st.text_input("Enter your Gemini API Key", type="password", 
                               help="Or set GEMINI_API_KEY in your .env file")
    else:
        st.success("API Key loaded from .env file")
    
    # Model settings section
    st.subheader("Model Settings")
    
    # Model selection
    model_options = {
        "gemini-2.0-flash": "Gemini 2.0 Flash (Fast)",
        "gemini-2.0-pro": "Gemini 2.0 Pro (Balanced)",
        "gemini-1.5-flash": "Gemini 1.5 Flash (Legacy)"
    }
    selected_model = st.selectbox(
        "Select Model", 
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    
    # Temperature setting
    temperature = st.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )
    
    # Max output tokens
    max_output_tokens = st.slider(
        "Max Output Tokens",
        min_value=100,
        max_value=8192,
        value=4096,
        step=100,
        help="Maximum number of tokens in the response"
    )
    
    # Reasoning settings section
    st.subheader("Reasoning Settings")
    
    # Toggle for enabling/disabling reasoning
    enable_reasoning = st.toggle("Enable Reasoning", value=True, 
                               help="Turn off to get direct responses without iterative reasoning")
    
    # Number of iterations slider (only shown if reasoning is enabled)
    max_iterations = 1  # Default if reasoning is disabled
    if enable_reasoning:
        max_iterations = st.slider(
            "Number of reasoning iterations", 
            min_value=1, 
            max_value=5, 
            value=3,
            help="More iterations may improve response quality but take longer"
        )
    
    # UI settings section
    st.subheader("UI Settings")
    
    # Show timestamps
    show_timestamps = st.toggle("Show timestamps", value=True,
                              help="Display timestamps for each message")
    
    # Option to auto-expand thinking process
    auto_expand_thinking = st.toggle("Auto-expand thinking process", value=False,
                                      help="Automatically expand the thinking process for each response")
    
    # Advanced settings
    st.subheader("Advanced Settings")
    
    # Top-p sampling
    top_p = st.slider(
        "Top-p", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.95, 
        step=0.05,
        help="Controls diversity of responses"
    )
    
    # Top-k sampling
    top_k = st.slider(
        "Top-k", 
        min_value=1, 
        max_value=100, 
        value=64, 
        step=1,
        help="Controls randomness in token selection"
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking_history" not in st.session_state:
    st.session_state.thinking_history = []

# Function to configure Gemini API
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    model_params = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": max_output_tokens,
    }
    return genai.GenerativeModel(selected_model, generation_config=model_params)

# Function to analyze query
def analyze_query(model, query, chat_history):
    # Format chat history for context
    formatted_history = ""
    for msg in chat_history[-5:]:  # Use last 5 messages for context
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n"
    
    analysis_prompt = f"""
    You are Reasonable AI, created by Hassan RJ who is a Full Stack Developer and GIAIC Student Leader.
    
    TASK: Analyze the user's query to understand what they're asking for.
    
    Recent conversation context:
    {formatted_history}
    
    Current query: "{query}"
    
    Analyze this query and determine:
    1. What is the user asking for?
    2. How detailed should the response be?
    3. What specific information should be included in the response?
    4. How should previous context be considered?
    
    Format your response as follows:
    QUERY_INTENT: [Brief description of what the user is asking for]
    DESIRED_DETAIL_LEVEL: [BRIEF, MODERATE, DETAILED]
    KEY_POINTS_TO_ADDRESS: [List the main points that should be addressed in the response]
    CONTEXT_CONSIDERATION: [How previous messages should influence the response]
    ANALYSIS: [Your detailed analysis of the query]
    """
    
    response = model.generate_content(analysis_prompt)
    return response.text

# Function to improve prompt with reasoning
def improve_prompt(model, original_query, iteration, max_iterations, chat_history, analysis):
    # Format chat history for context
    formatted_history = ""
    for msg in chat_history[-5:]:  # Use last 5 messages for context
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n"
    
    system_prompt = f"""
    You are an expert prompt engineer. Your task is to analyze and improve the following query.
    
    Recent conversation context:
    {formatted_history}
    
    Initial analysis:
    {analysis}
    
    Iteration: {iteration+1} of {max_iterations}
    
    Current query: "{original_query}"
    
    Your task:
    1. Analyze the query to understand the user's intent, considering the conversation context
    2. Identify any ambiguities or missing context
    3. Restructure and enhance the query to get the best possible response
    4. Make the prompt more specific, detailed, and clear
    5. Ensure the improved prompt will generate a substantial, detailed response
    
    Format your response as follows:
    ANALYSIS: [Your detailed analysis of the query]
    IMPROVED PROMPT: [The improved prompt]
    """
    
    response = model.generate_content(system_prompt)
    return response.text

# Function to generate final response
def generate_final_response(model, improved_prompt, chat_history, analysis):
    # Format chat history for context
    formatted_history = ""
    for msg in chat_history[-5:]:  # Use last 5 messages for context
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n"
    
    # Extract detail level from analysis
    detail_level = "DETAILED"
    if "DESIRED_DETAIL_LEVEL:" in analysis:
        if "BRIEF" in analysis:
            detail_level = "BRIEF"
        elif "MODERATE" in analysis:
            detail_level = "MODERATE"
    
    # Add context to the improved prompt
    prompt_with_context = f"""
    You are Reasonable AI, created by Hassan RJ who is a Full Stack Developer and GIAIC Student Leader.
    
    Recent conversation context:
    {formatted_history}
    
    Initial analysis:
    {analysis}
    
    Based on the above context and analysis, please respond to the following:
    {improved_prompt}
    
    IMPORTANT INSTRUCTIONS:
    1. Provide a {detail_level.lower()} response that directly addresses the query
    2. Even for simple greetings, provide a friendly, substantial response (not just "Hi" or "Hello")
    3. For questions, provide informative, well-structured answers
    4. Make sure your response is relevant to what the user is asking
    5. Avoid unnecessary information that doesn't relate to the query
    6. If the user is asking for a greeting, respond with a warm, friendly greeting
    7. If the user is acknowledging something, provide a meaningful acknowledgment
    """
    
    response = model.generate_content(prompt_with_context)
    return response.text

# Set up a container for the chat interface
chat_container = st.container()

# Display chat history (all previous messages)
with chat_container:
    for i, message in enumerate(st.session_state.messages):
        # Get timestamp if available and enabled
        timestamp = ""
        if show_timestamps and "timestamp" in message:
            timestamp = f"<small style='color: gray;'>{message['timestamp']}</small><br>"
        
        # Display user message
        if message["role"] == "user":
            with st.chat_message("user"):
                if show_timestamps:
                    st.markdown(timestamp, unsafe_allow_html=True)
                st.markdown(message["content"])
                
                # Display thinking process directly below the user message
                if i < len(st.session_state.messages) - 1 and message["role"] == "user":
                    thinking_idx = i // 2
                    if thinking_idx < len(st.session_state.thinking_history) and st.session_state.thinking_history[thinking_idx]:
                        thinking = st.session_state.thinking_history[thinking_idx]
                        with st.expander("Thinking Process", expanded=False):
                            for step_num, step in enumerate(thinking):
                                if step_num == 0:
                                    st.markdown("### Query Analysis")
                                else:
                                    st.markdown(f"### Iteration {step_num}")
                                st.markdown(step)
                                st.markdown("---")
        
        # Display assistant response
        elif message["role"] == "assistant":
            # Display assistant response
            with st.chat_message("assistant"):
                if show_timestamps:
                    st.markdown(timestamp, unsafe_allow_html=True)
                st.markdown(message["content"])

# Get user input
prompt = st.chat_input("What would you like to know?")

# Process user input
if prompt:
    # Add timestamp to the message
    current_time = time.strftime("%I:%M %p")
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": current_time
    })
    
    # Display user message (this will be shown at the bottom after all previous messages)
    with st.chat_message("user"):
        if show_timestamps:
            st.markdown(f"<small style='color: gray;'>{current_time}</small><br>", unsafe_allow_html=True)
        st.markdown(prompt)
    
    # Check if API key is provided
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter your Gemini API Key in the sidebar or add it to your .env file as GEMINI_API_KEY")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Please enter your Gemini API Key in the sidebar or add it to your .env file as GEMINI_API_KEY",
            "timestamp": current_time
        })
    else:
        try:
            # Configure Gemini API
            model = configure_genai(api_key)
            
            # Initialize thinking steps for this query
            thinking_steps = []
            
            # First API call: Analyze the query
            with st.spinner("Analyzing query..."):
                analysis = analyze_query(model, prompt, st.session_state.messages[:-1])
                thinking_steps.append(f"### Query Analysis\n{analysis}")
            
            # Show thinking process accordion (closed by default) BEFORE the response
            thinking_container = st.container()
            
            # Iterative reasoning process
            current_query = prompt
            
            # Perform reasoning iterations if enabled
            if enable_reasoning:
                for i in range(max_iterations):
                    with st.spinner(f"Thinking (Iteration {i+1}/{max_iterations})..."):
                        # Improve the prompt with context and analysis
                        reasoning_output = improve_prompt(
                            model, 
                            current_query, 
                            i, 
                            max_iterations,
                            st.session_state.messages[:-1],
                            analysis
                        )
                        thinking_steps.append(reasoning_output)
                        
                        # Extract the improved prompt
                        if "IMPROVED PROMPT:" in reasoning_output:
                            current_query = reasoning_output.split("IMPROVED PROMPT:")[1].strip()
            
            # Store thinking steps in session state
            st.session_state.thinking_history.append(thinking_steps)
            
            # Display thinking process in the container
            with thinking_container:
                with st.expander("Thinking Process", expanded=auto_expand_thinking):
                    for step_num, step in enumerate(thinking_steps):
                        if step_num == 0:
                            st.markdown("### Query Analysis")
                        else:
                            st.markdown(f"### Iteration {step_num}")
                        st.markdown(step)
                        st.markdown("---")
            
            # Generate final response with context and analysis
            response_time = time.strftime("%I:%M %p")
            with st.chat_message("assistant"):
                with st.spinner("Generating final response..."):
                    final_response = generate_final_response(
                        model, 
                        current_query,
                        st.session_state.messages[:-1],
                        analysis
                    )
                    if show_timestamps:
                        st.markdown(f"<small style='color: gray;'>{response_time}</small><br>", unsafe_allow_html=True)
                    st.markdown(final_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_response,
                "timestamp": response_time
            })
                
        except Exception as e:
            error_time = time.strftime("%I:%M %p")
            with st.chat_message("assistant"):
                if show_timestamps:
                    st.markdown(f"<small style='color: gray;'>{error_time}</small><br>", unsafe_allow_html=True)
                st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"An error occurred: {str(e)}",
                "timestamp": error_time
            })

# Add a reset button
if st.button("Reset Chat", key="reset_chat", help="Clear all chat history and start fresh"):
    st.session_state.messages = []
    st.session_state.thinking_history = []
    st.rerun()

