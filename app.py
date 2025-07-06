import streamlit as st
import pandas as pd
import re

# --- Title ---
st.set_page_config(page_title="Influencer Search", layout="wide")
st.title("🔍 Influencer Search App")

# --- Load Data ---
@st.cache_data
def load_data():
    df_main = pd.read_csv("df.csv")
    df_secondary = pd.read_csv("df2.csv")
    
    # Clean newline characters
    for col in ["NAME", "INF INSTAGRAM NAME"]:
        if col in df_main.columns:
            df_main[col] = df_main[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()

    for col in ["NAME", "INF"]:
        if col in df_secondary.columns:
            df_secondary[col] = df_secondary[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
    
    return df_main, df_secondary

df, df2 = load_data()

# --- Helper: Extract Handle from Link ---
def extract_instagram_handle(link):
    try:
        # Remove any tracking/query params
        clean_link = re.split(r'\?igsh|/\?h|\?h', link)[0]
        handle_part = clean_link.replace("https://www.instagram.com/", "").strip()
        handle = handle_part.rstrip("/").strip()
        return handle
    except Exception:
        return ""

# --- Search Section ---
st.markdown("### 🔎 Search Options")

search_type = st.selectbox(
    "How would you like to search?",
    ["Influencer Name", "Instagram Handle", "Instagram Link"]
)

query = st.text_input("Enter your search text:")

# --- On Search ---
if st.button("Search"):
    if query.strip() == "":
        st.warning("Please enter something to search.")
    else:
        if search_type == "Influencer Name":
            result1 = df[df["NAME"].str.contains(query, case=False, na=False)]
            result2 = df2[df2["NAME"].str.contains(query, case=False, na=False)]

            st.subheader("📁 Results from Dataset 1 (df.csv)")
            st.dataframe(result1)

            st.subheader("📁 Results from Dataset 2 (df2.csv)")
            st.dataframe(result2)

        elif search_type == "Instagram Handle":
            result1 = df2[df2["INF"].str.contains(query, case=False, na=False)]
            result2 = df[df["INF INSTAGRAM NAME"].str.contains(query, case=False, na=False)]

            st.subheader("📁 Results from Dataset 2 (df2.csv)")
            st.dataframe(result1)

            st.subheader("📁 Results from Dataset 1 (df.csv)")
            st.dataframe(result2)

        elif search_type == "Instagram Link":
            handle = extract_instagram_handle(query)
            if not handle:
                st.warning("Could not extract a valid Instagram handle from the provided link.")
            else:
                st.success(f"✅ Extracted Instagram Handle: **{handle}**")

                result1 = df2[df2["INF"].str.contains(handle, case=False, na=False)]
                result2 = df[df["INF INSTAGRAM NAME"].str.contains(handle, case=False, na=False)]

                st.subheader("📁 Results from Dataset 2 (df2.csv)")
                st.dataframe(result1)

                st.subheader("📁 Results from Dataset 1 (df.csv)")
                st.dataframe(result2)
