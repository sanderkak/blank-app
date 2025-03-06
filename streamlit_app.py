import streamlit as st

st.title("Demonstrating football skills for AZ")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

import requests
import pandas as pd

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

st.title("StatsBomb Open Data Explorer")

# Stap 1: Competities ophalen
competitions_url = f"{BASE_URL}/competitions.json"
competitions = requests.get(competitions_url).json()
df_competitions = pd.DataFrame(competitions)

# Competitie selecteren
competition_choice = st.selectbox("Selecteer een competitie", df_competitions['competition_name'])
selected_competition = df_competitions[df_competitions['competition_name'] == competition_choice].iloc[0]

competition_id = selected_competition['competition_id']
season_id = selected_competition['season_id']

# Stap 2: Wedstrijden ophalen
matches_url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"
matches = requests.get(matches_url).json()
df_matches = pd.DataFrame(matches)

# Wedstrijd selecteren
match_choice = st.selectbox("Selecteer een wedstrijd", df_matches['home_team'] + " vs " + df_matches['away_team'])
selected_match = df_matches[df_matches['home_team'] + " vs " + df_matches['away_team'] == match_choice].iloc[0]

match_id = selected_match['match_id']

# Stap 3: Eventdata ophalen
if st.button("Toon Event Data"):
    events_url = f"{BASE_URL}/events/{match_id}.json"
    events = requests.get(events_url).json()
    df_events = pd.DataFrame(events)
    st.write(df_events.head())


