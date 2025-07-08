import streamlit as st
import pandas as pd
import re
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Influencer Search", layout="wide")
st.title("🔍 Influencer Search App")

# --- Load Data ---
@st.cache_data
def load_data():
    df_main = pd.read_csv("df.csv")
    df_secondary = pd.read_csv("df2.csv")

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

# --- App Navigation ---
page = st.radio("Choose Page:", ["🔍 Search", "📊 Plots"])

# --- Search Page ---
if page == "🔍 Search":
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

    query = ""
    dropdown_selection = None
    search_mode = None

    if search_type in ["Search by Category", "Search by Source"]:
        search_mode = st.radio("Choose Input Method:", ["Dropdown", "Write Text"])

    if search_type in ["Influencer Name", "Instagram Handle", "Instagram Link"]:
        query = st.text_input("Enter your search text:")
    elif search_type == "Search by Category":
        if search_mode == "Dropdown":
            available_categories = sorted(df["Category"].dropna().unique())
            dropdown_selection = st.selectbox("Choose a Category:", [""] + available_categories)
        else:
            query = st.text_input("Enter category name:")
    elif search_type == "Search by Source":
        if search_mode == "Dropdown":
            available_sources = sorted(df["SOURCE"].dropna().unique())
            dropdown_selection = st.selectbox("Choose a Source:", [""] + available_sources)
        else:
            query = st.text_input("Enter source name:")

    if st.button("Search"):
        if (search_type in ["Influencer Name", "Instagram Handle", "Instagram Link"] or search_mode == "Write Text") and query.strip() == "":
            st.warning("Please enter something to search.")
        elif search_mode == "Dropdown" and (not dropdown_selection or dropdown_selection.strip() == ""):
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
                value = dropdown_selection if search_mode == "Dropdown" else query
                result1 = df[df["Category"].str.contains(value, case=False, na=False)]
                result2 = pd.DataFrame()

            elif search_type == "Search by Source":
                value = dropdown_selection if search_mode == "Dropdown" else query
                result1 = df[df["SOURCE"].str.contains(value, case=False, na=False)]
                result2 = pd.DataFrame()

            # Display Results
            st.subheader("📁 All Data (df.csv)")
            st.dataframe(result2 if search_type in ["Instagram Handle", "Instagram Link"] else result1)

            if not result2.empty or search_type in ["Instagram Handle", "Instagram Link", "Influencer Name"]:
                st.subheader("📁 Instagram Answer (df2.csv)")
                st.dataframe(result1)

# --- Plot Page ---
elif page == "📊 Plots":
    st.markdown("### 📊 Data Visualizations")
    plot_option = st.radio("Select Plot:", ["Followers", "Source", "Category"])

    if plot_option == "Followers":
        if "Followers" in df.columns:
            st.write("Distribution of Followers")
            fig = px.histogram(df, x="Followers", nbins=30, title="Followers Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Followers column not found in the dataset.")

    elif plot_option == "Source":
        if "SOURCE" in df.columns:
            st.write("Influencer Count by Source")
            source_counts = df["SOURCE"].value_counts().reset_index()
            source_counts.columns = ["Source", "Count"]
            fig = px.bar(source_counts, x="Source", y="Count", title="Source Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("SOURCE column not found.")

    elif plot_option == "Category":
        if "Category" in df.columns:
            st.write("Influencer Count by Category")
            cat_counts = df["Category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.bar(cat_counts, x="Category", y="Count", title="Category Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Category column not found.")
