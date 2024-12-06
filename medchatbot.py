# %%
import pandas as pd
import re
import spacy
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

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        margin: 5px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #4CAF50;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #E8F5E9;
        text-align: right;
    }
    .bot-message {
        background-color: #F0F8FF;
        text-align: left;
    }
    .example-button {
        display: inline-block;
        margin: 5px;
        padding: 10px;
        background-color: #E8F5E9;
        border-radius: 5px;
        cursor: pointer;
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

    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")

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
        doc = nlp(text)
        found_terms = [token.text for token in doc if token.text.lower() in include_keywords]
        
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

# Chatbot greetings
def get_greeting_response(text):
    text = text.lower()
    if "hi" in text or "hello" in text:
        return "👋 Hello! I'm your Medical Query Assistant. How can I help you today? You can describe your symptoms or click on example queries below."
    return None

# Streamlit Interface
def main():
    # Header with styling
    st.markdown("<h1 style='text-align: center; color: #2E8B57;'>🏥 Medical Boolean Query Generator</h1>", unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<p style='color: #4CAF50; font-size: 20px;'>Enter medical symptoms or conditions to generate a Boolean search query</p>", unsafe_allow_html=True)
        
        # Text input with custom styling
        user_input = st.text_area("Enter text:", "", height=150)
        
        # Display chat history
        for message in st.session_state.chat_history:
            st.markdown(f"<div class='chat-message {message['type']}-message'>{message['text']}</div>", unsafe_allow_html=True)
        
        if st.button("🔍 Generate Query", key="generate"):
            if user_input:
                # Check for greetings
                greeting = get_greeting_response(user_input)
                if greeting:
                    st.session_state.chat_history.append({"text": user_input, "type": "user"})
                    st.session_state.chat_history.append({"text": greeting, "type": "bot"})
                else:
                    with st.spinner("Generating query..."):
                        cleaned_text = clean_text(user_input)
                        query = generate_boolean_query(cleaned_text)
                    
                    st.session_state.chat_history.append({"text": user_input, "type": "user"})
                    st.session_state.chat_history.append({"text": f"Generated Query: {query}", "type": "bot"})
                    
                    # Add query to history
                    if 'query_history' not in st.session_state:
                        st.session_state.query_history = []
                    st.session_state.query_history.append(query)
            else:
                st.warning("⚠️ Please enter some text")
    
    with col2:
        # Example queries with clickable buttons
        st.markdown("<h3 style='color: #2E8B57;'>Example Queries</h3>", unsafe_allow_html=True)
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
        
        # Query History
        if 'query_history' in st.session_state and st.session_state.query_history:
            st.markdown("<h3 style='color: #2E8B57;'>Recent Queries</h3>", unsafe_allow_html=True)
            for q in st.session_state.query_history[-5:]:  # Show only last 5 queries
                st.markdown(f"<div style='padding: 10px; background-color: #E8F5E9; border-radius: 5px; margin: 5px;'>{q}</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center;'>
            <p>Made with ❤️ by Team Justice League</p>
            <p style='font-size: 18px; font-weight: bold; color: #2E8B57;'>Development Team:</p>
            <p>Lead Developer: Vikhram S</p>
            <p>Co-Developers: Sanjay B & Sree Dharma</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
