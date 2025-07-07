import streamlit as st
import pandas as pd
import re

# --- Page Setup ---
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
    [
        "Influencer Name",
        "Instagram Handle",
        "Instagram Link",
        "Search by Category",
        "Search by Source"
    ]
)

# --- Logic Based on Search Type ---
query = ""
dropdown_selection = None

if search_type in ["Influencer Name", "Instagram Handle", "Instagram Link"]:
    query = st.text_input("Enter your search text:")
elif search_type == "Search by Category":
    available_categories = sorted(df["category"].dropna().unique())
    dropdown_selection = st.selectbox("Choose a category:", [""] + available_categories)
elif search_type == "Search by Source":
    available_sources = sorted(df["source"].dropna().unique())
    dropdown_selection = st.selectbox("Choose a source:", [""] + available_sources)

# --- On Search ---
if st.button("Search"):
    if search_type in ["Influencer Name", "Instagram Handle", "Instagram Link"] and query.strip() == "":
        st.warning("Please enter something to search.")
    elif search_type in ["Search by Category", "Search by Source"] and (not dropdown_selection or dropdown_selection.strip() == ""):
        st.warning("Please choose an option from the dropdown.")
    else:
        if search_type == "Influencer Name":
            result1 = df[df["NAME"].str.contains(query, case=False, na=False)]
            result2 = df2[df2["NAME"].str.contains(query, case=False, na=False)]

        elif search_type == "Instagram Handle":
            result1 = df2[df2["INF"].str.contains(query, case=False, na=False)]
            result2 = df[df["INF INSTAGRAM NAME"].str.contains(query, case=False, na=False)]

        elif search_type == "Instagram Link":
            handle = extract_instagram_handle(query)
            if not handle:
                st.warning("Could not extract a valid Instagram handle from the provided link.")
                result1 = result2 = pd.DataFrame()
            else:
                st.success(f"✅ Extracted Instagram Handle: **{handle}**")
                result1 = df2[df2["INF"].str.contains(handle, case=False, na=False)]
                result2 = df[df["INF INSTAGRAM NAME"].str.contains(handle, case=False, na=False)]

        elif search_type == "Search by Category":
            result1 = df[df["category"] == dropdown_selection]
            result2 = pd.DataFrame()  # No Instagram answer here

        elif search_type == "Search by Source":
            result1 = df[df["source"] == dropdown_selection]
            result2 = pd.DataFrame()  # No Instagram answer here

        # Display results
        st.subheader("📁 All Data (df.csv)")
        st.dataframe(result2 if search_type in ["Instagram Handle", "Instagram Link"] else result1)

        if not result2.empty:
            st.subheader("📁 Instagram Answer (df2.csv)")
            st.dataframe(result1)
        elif search_type in ["Instagram Handle", "Instagram Link", "Influencer Name"]:
            st.subheader("📁 Instagram Answer (df2.csv)")
            st.dataframe(result1)
