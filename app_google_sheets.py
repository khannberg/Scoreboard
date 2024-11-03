import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

# Load credentials from Streamlit secrets and define the scope
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Define credentials with the correct scope
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# Attempt to open the Google Sheet
try:
    sheet = client.open("MMA Scorecard Sheets Integration").sheet1
    data = sheet.get_all_records()
    st.write("Data fetched successfully:", data)
except Exception as e:
    st.write("An error occurred:", e)
