# %%
import pandas as pd
import re
from nltk.corpus import stopwords
import nltk
import random
import streamlit as st

# Set page configuration and styling
st.set_page_config(
    page_title="Medical Boolean Query Generator",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS styling with dark/light mode compatibility
st.markdown("""
    <style>
    .main {
        background-color: transparent;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: var(--text-color);
        border-radius: 10px;
        padding: 10px 20px;
        margin: 5px;
        transition: transform 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #4CAF50;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        animation: fadeIn 0.5s ease;
    }
    .user-message {
        background-color: rgba(76, 175, 80, 0.2);
        text-align: right;
    }
    .bot-message {
        background-color: rgba(100, 149, 237, 0.2);
        text-align: left;
    }
    .example-button {
        display: inline-block;
        margin: 5px;
        padding: 10px;
        background-color: rgba(76, 175, 80, 0.2);
        border-radius: 5px;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

try:
    # Load the dataset
    df = pd.read_csv("C:/Users/hpsli/Favorites/Downloads/MIETIC_v1.csv")
    df_cleaned = df.dropna()
    data = df_cleaned

    # Download NLTK stopwords if not already downloaded
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

except Exception as e:
    st.error(f"Error loading dependencies: {str(e)}")
    st.stop()

# Define function to clean text
def clean_text(text):
    try:
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.lower()
        text = ' '.join([word for word in text.split() if word not in stop_words])
        return text
    except Exception as e:
        st.error(f"Error cleaning text: {str(e)}")
        return ""

# Keywords lists
include_keywords = [
    "pain", "fever", "hypertension", "infection", "cough", "dyspnea", "nausea", 
    "vomiting", "fatigue", "weakness", "dizziness", "diarrhea", "constipation",
    "swelling", "headache", "chest pain", "abdominal pain", "shortness of breath",
    "joint pain", "muscle pain", "rash", "itching", "loss of consciousness",
    "palpitations", "seizure", "edema", "anxiety", "depression", "insomnia",
    "confusion", "fainting", "hypotension", "diabetes", "cancer", "asthma"
]

exclude_keywords = ["medical"]

# Function to generate Boolean queries
def generate_boolean_query(text):
    try:
        # Split text into words and find matching keywords
        words = text.split()
        found_terms = [word for word in words if word.lower() in include_keywords]
        
        # Ensure at least 3 terms
        while len(found_terms) < 3:
            found_terms.append(random.choice(include_keywords))
            
        and_terms = found_terms[:2]
        or_term = found_terms[2] 
        not_term = random.choice(exclude_keywords)
        
        query = f"{and_terms[0]} AND {and_terms[1]} OR {or_term} NOT {not_term}"
        return query
        
    except Exception as e:
        st.error(f"Error generating query: {str(e)}")
        return ""

# Enhanced chatbot greetings
def get_greeting_response(text):
    text = text.lower()
    greetings = {
        "hi": "👋 Hello! I'm your Medical Query Assistant. How can I help you today?",
        "hello": "👋 Hi there! I'm here to help with your medical queries.",
        "hey": "👋 Hey! Ready to assist you with medical information.",
        "good morning": "🌅 Good morning! How may I assist you today?",
        "good afternoon": "☀️ Good afternoon! How can I help you?",
        "good evening": "🌆 Good evening! What medical queries can I help you with?"
    }
    
    for greeting in greetings:
        if greeting in text:
            return f"{greetings[greeting]} You can describe your symptoms or click on example queries below."
    return None

# Streamlit Interface
def main():
    # Default greeting
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
        st.balloons()
    
    # Header with styling
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🏥 Medical Boolean Query Generator</h1>", unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # Add default welcome message
        st.session_state.chat_history.append({
            "text": "👋 Welcome! I'm your Medical Query Assistant. How can I help you today?",
            "type": "bot"
        })
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<p style='color: #4CAF50; font-size: 20px;'>Enter medical symptoms or conditions to generate a Boolean search query</p>", unsafe_allow_html=True)
        
        # Text input with custom styling
        user_input = st.text_area("Enter text:", "", height=150)
        
        # Display chat history with animations
        for message in st.session_state.chat_history:
            st.markdown(f"<div class='chat-message {message['type']}-message'>{message['text']}</div>", unsafe_allow_html=True)
        
        if st.button("🔍 Generate Query", key="generate"):
            if user_input:
                st.success("Processing your query...")
                # Check for greetings
                greeting = get_greeting_response(user_input)
                if greeting:
                    st.session_state.chat_history.append({"text": user_input, "type": "user"})
                    st.session_state.chat_history.append({"text": greeting, "type": "bot"})
                else:
                    with st.spinner("🔄 Generating query..."):
                        cleaned_text = clean_text(user_input)
                        query = generate_boolean_query(cleaned_text)
                    
                    st.session_state.chat_history.append({"text": user_input, "type": "user"})
                    st.session_state.chat_history.append({"text": f"Generated Query: {query}", "type": "bot"})
                    
                    # Add query to history with animation
                    if 'query_history' not in st.session_state:
                        st.session_state.query_history = []
                    st.session_state.query_history.append(query)
                    st.snow()
            else:
                st.warning("⚠️ Please enter some text")
    
    with col2:
        # Example queries with enhanced styling
        st.markdown("<h3 style='color: #4CAF50;'>Example Queries</h3>", unsafe_allow_html=True)
        example_queries = {
            "🤒 Fever & Cough": "Patient with fever and cough",
            "🤕 Headache": "Severe headache with nausea",
            "💔 Chest Issues": "Chest pain and shortness of breath",
            "🦠 Infection": "Infection with fever and weakness",
            "😴 Sleep Issues": "Insomnia with anxiety and depression"
        }
        
        for label, query in example_queries.items():
            if st.button(label):
                cleaned_text = clean_text(query)
                generated_query = generate_boolean_query(cleaned_text)
                st.session_state.chat_history.append({"text": f"Example: {query}", "type": "user"})
                st.session_state.chat_history.append({"text": f"Generated Query: {generated_query}", "type": "bot"})
                st.balloons()
        
        # Query History with enhanced styling
        if 'query_history' in st.session_state and st.session_state.query_history:
            st.markdown("<h3 style='color: #4CAF50;'>Recent Queries</h3>", unsafe_allow_html=True)
            for q in st.session_state.query_history[-5:]:
                st.markdown(f"<div style='padding: 10px; background-color: rgba(76, 175, 80, 0.2); border-radius: 5px; margin: 5px;'>{q}</div>", unsafe_allow_html=True)

    # Footer with enhanced styling
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center;'>
            <p>Made with ❤️ by Team Justice League</p>
            <p style='font-size: 18px; font-weight: bold; color: #4CAF50;'>Development Team:</p>
            <p>Lead Developer: Vikhram S</p>
            <p>Co-Developers: Sanjay B & Sree Dharma</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
