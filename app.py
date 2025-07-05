import streamlit as st
import pandas as pd
import re
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials
import json
import os

# -----------------------------------
# Load Google Sheets using Service Account
# -----------------------------------

# Load credentials from Streamlit Cloud secrets
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(creds)

# Open the spreadsheet and load worksheets
sheet_url = "https://docs.google.com/spreadsheets/d/1G9G5LAYAMwmofYKW7YnCtPc5yfnymwC3xxiUjxrYpqs"
spreadsheet = gc.open_by_url(sheet_url)
worksheet1 = spreadsheet.worksheet("ALL DATA TABLE")
worksheet2 = spreadsheet.worksheet("INSTAGRAM ANSWER")

df = get_as_dataframe(worksheet1, evaluate_formulas=True, skip_empty_rows=False).dropna(how='all')
df2 = get_as_dataframe(worksheet2, evaluate_formulas=True, skip_empty_rows=False).dropna(how='all')

# Clean newline characters
df["NAME"] = df["NAME"].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
df["INF INSTAGRAM NAME"] = df["INF INSTAGRAM NAME"].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
df2["NAME"] = df2["NAME"].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
df2["INF"] = df2["INF"].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()

# -----------------------------------
# Helper to extract handle from Instagram link
# -----------------------------------
def extract_instagram_handle(link):
    if not isinstance(link, str):
        return None
    clean_link = re.split(r'[\?]|/$', link)[0]
    handle = clean_link.replace("https://www.instagram.com/", "")
    handle = handle.replace("http://www.instagram.com/", "")
    return handle.strip().strip("/")

# -----------------------------------
# Streamlit UI
# -----------------------------------
st.title("Influencer Search App")

search_type = st.selectbox(
    "How would you like to search?",
    ["Influencer Name", "Instagram Handle", "Instagram Link"]
)

query = st.text_input("Enter your search text:")

if st.button("Search"):
    if query.strip() == "":
        st.warning("Please enter something to search.")
    else:
        if search_type == "Influencer Name":
            result1 = df[df["NAME"].str.contains(query, case=False, na=False)]
            result2 = df2[df2["NAME"].str.contains(query, case=False, na=False)]

            st.subheader("Results from Dataset 1 (df)")
            st.write(result1)

            st.subheader("Results from Dataset 2 (df2)")
            st.write(result2)

        elif search_type == "Instagram Handle":
            result1 = df2[df2["INF"].str.contains(query, case=False, na=False)]
            result2 = df[df["INF INSTAGRAM NAME"].str.contains(query, case=False, na=False)]

            st.subheader("Results from Dataset 2 (df2)")
            st.write(result1)

            st.subheader("Results from Dataset 1 (df)")
            st.write(result2)

        elif search_type == "Instagram Link":
            handle = extract_instagram_handle(query)
            st.info(f"Extracted handle: **{handle}**")

            if handle:
                result1 = df2[df2["INF"].str.contains(handle, case=False, na=False)]
                result2 = df[df["INF INSTAGRAM NAME"].str.contains(handle, case=False, na=False)]

                st.subheader("Results from Dataset 2 (df2)")
                st.write(result1)

                st.subheader("Results from Dataset 1 (df)")
                st.write(result2)
            else:
                st.warning("Could not extract a valid Instagram handle from the link.")
