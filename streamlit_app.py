import re
import bisect
import requests
import pandas as pd
import streamlit as st
from io import BytesIO
from bs4 import BeautifulSoup

BASE_URL = "https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
}

# ------------------------------------------------------------------------------------
# Step 1: Fetch and prepare data
# ------------------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_data() -> tuple:
    """
    Fetches the latest ODS decision file from ireland.ie and returns
    a cleaned DataFrame and the period label string.
    Returns (df, period_label) or (None, error_message).
    """
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, str(e)

    soup = BeautifulSoup(resp.content, "html.parser")

    # Find the link — flexible match: any "Visa decisions made from … January …" link
    file_url = None
    period_label = None
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        if re.search(r"Visa decisions made from.*January", text, re.IGNORECASE):
            file_url = link.get("href", "")
            period_label = text
            if not file_url.startswith("http"):
                file_url = requests.compat.urljoin(BASE_URL, file_url)
            break

    if not file_url:
        return None, "Could not find the visa decisions file on the website."

    try:
        r2 = requests.get(file_url, headers=HEADERS, timeout=30)
        r2.raise_for_status()
    except requests.RequestException as e:
        return None, str(e)

    try:
        raw = pd.read_excel(BytesIO(r2.content), engine="odf", header=None)
    except Exception as e:
        return None, f"Failed to parse ODS file: {e}"

    # Locate header row dynamically
    header_row = None
    for i, row in raw.iterrows():
        vals = [str(v).lower() for v in row.values]
        if any("application number" in v for v in vals):
            header_row = i
            break

    if header_row is None:
        return None, "Could not locate the 'Application Number' header in the file."

    df = raw.iloc[header_row + 1:].copy()
    df = df.iloc[:, 2:4].copy()
    df.columns = ["Application Number", "Decision"]
    df.dropna(how="all", inplace=True)

    # Remove any duplicate header rows left in the data
    df = df[df["Application Number"].astype(str).str.strip().str.lower() != "application number"]
    df.reset_index(drop=True, inplace=True)

    df["Application Number"] = df["Application Number"].astype(str).str.strip().astype(int)
    df["Decision"] = df["Decision"].astype(str).str.strip()
    df.sort_values(by="Application Number", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df, period_label


# ------------------------------------------------------------------------------------
# Step 2: Binary search for nearest application numbers
# ------------------------------------------------------------------------------------

def binary_search_nearest(df, target):
    """Binary search for nearest application numbers before and after target."""
    numbers = df["Application Number"].tolist()
    pos = bisect.bisect_left(numbers, target)
    before = numbers[pos - 1] if pos > 0 else None
    after = numbers[pos] if pos < len(numbers) else None
    return before, after


# ------------------------------------------------------------------------------------
# Step 3: Search UI
# ------------------------------------------------------------------------------------

def search_application(df):
    """Render the search input and display the result."""
    user_input = st.text_input(
        "Enter your Application Number (e.g. 63690452 or IRL63690452):",
        max_chars=11,
    )

    if not user_input:
        return

    raw = user_input.strip()

    # Parse and validate
    if raw.upper().startswith("IRL"):
        numeric = raw[3:]
    else:
        numeric = raw

    if not numeric.isdigit():
        st.error("❌ Only digits are allowed (with optional IRL prefix). Example: `IRL63690452`")
        return
    if len(numeric) < 8:
        st.warning(f"❌ Too short ({len(numeric)} digits). Must be exactly 8 digits.")
        return
    if len(numeric) > 8:
        st.warning(f"❌ Too long ({len(numeric)} digits). Must be exactly 8 digits.")
        return

    application_number = int(numeric)
    result = df[df["Application Number"] == application_number]

    if not result.empty:
        decision = result.iloc[0]["Decision"]
        d = decision.lower()
        if "approv" in d or "grant" in d:
            st.success(f"**Application {application_number} — Decision: {decision}** ✅")
        elif "refus" in d or "reject" in d:
            st.error(f"**Application {application_number} — Decision: {decision}** ❌")
        else:
            st.info(f"**Application {application_number} — Decision: {decision}**")
        return

    st.warning(f"No record found for Application Number: {application_number}.")

    before, after = binary_search_nearest(df, application_number)

    rows = []
    if before:
        dec = df[df["Application Number"] == before]["Decision"].values[0]
        rows.append({"Position": "Before", "Application Number": before, "Decision": dec, "Difference": application_number - before})
    if after:
        dec = df[df["Application Number"] == after]["Decision"].values[0]
        rows.append({"Position": "After", "Application Number": after, "Decision": dec, "Difference": after - application_number})

    if rows:
        st.subheader("Nearest Application Numbers")
        header = "| Position | Application Number | Decision | Difference |\n|---|---|---|---|"
        body = "\n".join(
            f"| {r['Position']} | {r['Application Number']} | {r['Decision']} | {r['Difference']} |"
            for r in rows
        )
        st.markdown(f"{header}\n{body}")
    else:
        st.info("No nearest application numbers found.")


# ------------------------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Ireland Visa Status Checker",
        page_icon="🇮🇪",
        layout="centered",
    )

    st.title("🇮🇪 Ireland Visa Application Status Checker")
    st.caption("New Delhi Embassy · Data sourced from ireland.ie")

    with st.expander("How to use"):
        st.markdown("""
        1. Enter your 8-digit application number — with or without the `IRL` prefix.
        2. Click anywhere or press Enter to search.
        3. If your number isn't in the list yet, the app shows the nearest processed numbers above and below yours.
        """)

    with st.spinner("Loading latest visa decisions…"):
        df, meta = load_data()

    if df is None:
        st.error(f"Could not load data: {meta}")
        st.stop()

    st.success(f"**{meta}**")

    total = len(df)
    decisions = df["Decision"].value_counts()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Decisions", total)
    col2.metric("Approved", int(decisions.get("Approved", 0)))
    col3.metric("Refused", int(decisions.get("Refused", 0)))

    st.divider()
    search_application(df)
    st.divider()

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download full dataset (CSV)",
        data=csv,
        file_name="ireland_visa_decisions_newdelhi.csv",
        mime="text/csv",
    )

    st.caption(f"Data refreshes every hour. [Source]({BASE_URL})")


if __name__ == "__main__":
    main()
