import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

st.header("MMA Scorecard", divider="blue")

# Google Sheets credentials fra Streamlit Secrets (til brug på Streamlit Cloud)
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])

# Definer scopes for Google Sheets og Google Drive
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Initialiser credentials med de definerede scopes
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# Åbn Google Sheet (udskift "Your Google Sheet Name" med navnet på dit Google Sheet)
sheet = client.open("MMA Scorecard Sheets Integration").sheet1

# Funktion til at gemme resultater til Google Sheets
def save_results_to_google_sheets(results, player1_name, player2_name, overall_total_player1, overall_total_player2, notes):
    # Tilføj en række til Google Sheets for hvert resultat
    for result in results:
        round_info, p1_score, p2_score = result
        sheet.append_row([round_info, player1_name, p1_score, player2_name, p2_score, overall_total_player1, overall_total_player2, notes])

# Scoreboard calculation
df = pd.DataFrame({
    'player 1': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'player 2': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
})

# Initialize session_state for "Notes" and results if they don't already exist
if "name" not in st.session_state:
    st.session_state.name = ""  # Initialize notes with an empty value
if "results" not in st.session_state:
    st.session_state.results = []  # Initialize results as an empty list

# Input player names
player1_name = st.text_input("Name for the red team", value="Player 1")
player2_name = st.text_input("Name for the blue team", value="Player 2")

# Lists to store each round's total for each player
player1_scores = []
player2_scores = []

# Input form
with st.form(key='columns_in_form'):
    for i in range(1, 6):  # Loop through 5 rounds
        col1, col_mid, col2 = st.columns([1, 0.2, 1])  # Two columns with spacing for round text

        # Player 1's input for each round
        with col1:
            st.markdown(f"<h3 style='background-color:#FFCCCC; padding: 10px; border-radius: 5px;'>{player1_name} - Round {i}</h3>", unsafe_allow_html=True)
            plus = st.selectbox('Round Score', df['player 1'], key=f'plus_player_1_round_{i}')   
            minus = st.selectbox('Point Deduct', df['player 1'], key=f'minus_player_1_round_{i}') 
            player1_total = plus - minus  # Calculate score for this round
            player1_scores.append(player1_total)

        # Player 2's input for each round
        with col2:
            st.markdown(f"<h3 style='background-color:#CCCCFF; padding: 10px; border-radius: 5px;'>{player2_name} - Round {i}</h3>", unsafe_allow_html=True)
            plus2 = st.selectbox('Round Score', df['player 2'], key=f'plus_player_2_round_{i}')   
            minus2 = st.selectbox('Point Deduct', df['player 2'], key=f'minus_player_2_round_{i}')
            player2_total = plus2 - minus2  # Calculate score for this round
            player2_scores.append(player2_total)

    # Total button
    submitButton = st.form_submit_button(label='Total')

# Calculate and store total in session_state when button is pressed
if submitButton:
    overall_total_player1 = sum(player1_scores)
    overall_total_player2 = sum(player2_scores)

    # Store the results as a list of tuples in session_state
    results = [(f"Round {i}", p1_score, p2_score) for i, (p1_score, p2_score) in enumerate(zip(player1_scores, player2_scores), 1)]
    st.session_state.results = results
    st.session_state.overall_total_player1 = overall_total_player1
    st.session_state.overall_total_player2 = overall_total_player2

# Display stored results if they exist
if st.session_state.results:
    st.write("### Results:")
    for i, p1_score, p2_score in st.session_state.results:
        st.write(f"{i} - {player1_name} Score: {p1_score} | {player2_name} Score: {p2_score}")
    
    st.write(f"**Overall Total for {player1_name}:** {st.session_state.overall_total_player1}")
    st.write(f"**Overall Total for {player2_name}:** {st.session_state.overall_total_player2}")

# Notes field that uses session_state to retain data
note = st.text_input("Notes", key="name")

# "Save" button to save results to Google Sheets
if st.button("Save"):
    if st.session_state.results:
        # Save the results and notes to Google Sheets
        save_results_to_google_sheets(
            st.session_state.results,
            player1_name,
            player2_name,
            st.session_state.overall_total_player1,
            st.session_state.overall_total_player2,
            st.session_state.name
        )
        st.success("Results saved to Google Sheets!")
    else:
        st.warning("No results to save. Please calculate totals first.")

# Display the saved note
st.write("Current note:", st.session_state.name)
