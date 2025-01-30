import streamlit as st
import pandas as pd
import bisect
import requests
from io import BytesIO
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------------
# Step 1: Load Data (Fetch and Prepare the DataFrame)
# ------------------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_ods_file():
    """
    Fetches the .ods file from the visa decisions website and returns its binary content.

    Returns:
        - A BytesIO object containing the file content if successful.
        - None if the file could not be fetched.
    """
    url = "https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')

        # Find the link containing the specific text
        file_url = None
        for link in links:
            if "Visa decisions made from 1 January 2025 to" in link.get_text(strip=True):
                file_url = link.get('href')
                break

        if file_url:
            # Resolve relative URLs to absolute
            if not file_url.startswith("http"):
                file_url = requests.compat.urljoin(url, file_url)

            file_response = requests.get(file_url, headers=headers)
            if file_response.status_code == 200:
                return BytesIO(file_response.content)
    return None

@st.cache_data
def prepare_dataframe(file):
    """
    Prepares and cleans the DataFrame from the fetched .ods file.

    Args:
        file: The .ods file content as BytesIO.

    Returns:
        A cleaned and sorted DataFrame ready for searching.
    """
    df = pd.read_excel(file, engine='odf')
    df.drop(columns=["Unnamed: 0", "Unnamed: 1"], inplace=True, errors="ignore")
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Identify the header row
    for idx, row in df.iterrows():
        if row["Unnamed: 2"] == "Application Number" and row["Unnamed: 3"] == "Decision":
            df.columns = ["Application Number", "Decision"]
            df = df.iloc[idx + 1:]  # Skip the header row
            break

    # Process application numbers and sort the DataFrame
    df["Application Number"] = df["Application Number"].astype(str).str.strip().astype(int)
    df.sort_values(by="Application Number", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

# ------------------------------------------------------------------------------------
# Step 2: Binary Search Utility for Finding Nearest Application Numbers
# ------------------------------------------------------------------------------------

def binary_search_nearest(df, target):
    """
    Uses binary search to find the nearest application numbers in the DataFrame.

    Args:
        df: The DataFrame containing the application numbers.
        target: The target application number to search for.

    Returns:
        Two nearest application numbers (before and after the target).
    """
    application_numbers = df["Application Number"].tolist()
    pos = bisect.bisect_left(application_numbers, target)

    before = application_numbers[pos - 1] if pos > 0 else None
    after = application_numbers[pos] if pos < len(application_numbers) else None

    return before, after

# ------------------------------------------------------------------------------------
# Step 3: Search Application Status
# ------------------------------------------------------------------------------------

def search_application(df):
    """
    Handles the user input and searches for the application number in the DataFrame.

    Args:
        df: The DataFrame containing application numbers and decisions.
    """
    user_input = st.text_input("Enter your Application Number (including IRL if applicable):")

    if user_input:
        # Validate user input
        if "irl" in user_input.lower():
            try:
                application_number = int("".join(filter(str.isdigit, user_input.lower().split("irl")[-1])))
                if len(str(application_number)) < 8:
                    st.warning("Please enter a valid application number with at least 8 digits after IRL.")
                    return
            except ValueError:
                st.error("Invalid input after IRL. Please enter only digits.")
                return
        else:
            if not user_input.isdigit() or len(user_input) < 8:
                st.warning("Please enter at least 8 digits for your VISA application number.")
                return
            elif len(user_input) > 8:
                st.warning("The application number cannot exceed 8 digits. Please correct your input.")
                return
            application_number = int(user_input)

        # Search for the application number in the DataFrame
        result = df[df["Application Number"] == application_number]

        if not result.empty:
            decision = result.iloc[0]["Decision"]
            if decision.lower() == "refused":
                st.error(f"Application Number: {application_number}\n\nDecision: **Refused**")
            elif decision.lower() == "approved":
                st.success(f"Application Number: {application_number}\n\nDecision: **Approved**")
            else:
                st.info(f"Application Number: {application_number}\n\nDecision: **{decision}**")
        else:
            st.warning(f"No record found for Application Number: {application_number}.")

            # Find nearest application numbers using binary search
            before, after = binary_search_nearest(df, application_number)

            nearest_records = pd.DataFrame({
                "Nearest Application": ["Before", "After"],
                "Application Number": [before, after],
                "Decision": [
                    df[df["Application Number"] == before]["Decision"].values[0] if before else None,
                    df[df["Application Number"] == after]["Decision"].values[0] if after else None
                ],
                "Difference": [
                    application_number - before if before else None,
                    after - application_number if after else None
                ]
            }).dropna()

            if not nearest_records.empty:
                st.subheader("Nearest Application Numbers")
                st.table(nearest_records.reset_index(drop=True))
            else:
                st.info("No nearest application numbers found.")

# ------------------------------------------------------------------------------------
# Main Streamlit Application Logic
# ------------------------------------------------------------------------------------

def main():
    st.title("Visa Application Status Checker")

    # Fetch and prepare the data
    ods_file = fetch_ods_file()
    if ods_file:
        df = prepare_dataframe(ods_file)
        if df is not None:
            search_application(df)
        else:
            st.error("Failed to prepare the data.")
    else:
        st.error("Failed to fetch the .ods file.")

if __name__ == "__main__":
    main()
