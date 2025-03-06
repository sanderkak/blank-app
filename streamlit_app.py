import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch


# URLs for StatsBomb Open Data
BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/"
COMPETITIONS_URL = BASE_URL + "competitions.json"
MATCHES_URL = BASE_URL + "matches/{competition_id}/{season_id}.json"
EVENTS_URL = BASE_URL + "events/{match_id}.json"

# Functies om data te laden
def load_competitions():
    response = requests.get(COMPETITIONS_URL)
    return pd.DataFrame(response.json())


def load_matches(competition_id, season_id):
    url = MATCHES_URL.format(competition_id=competition_id, season_id=season_id)
    response = requests.get(url)
    return pd.DataFrame(response.json())


def load_events(match_id):
    url = EVENTS_URL.format(match_id=match_id)
    response = requests.get(url)
    return pd.DataFrame(response.json())

# Data ophalen
competitions = load_competitions()


match_files = []
for _, comp in competitions.iterrows():
    if comp['competition_id'] == 9 and comp['season_id'] == 281:
        matches = load_matches(comp['competition_id'], comp['season_id'])
        match_files.append(matches)

bayer_lever = pd.concat(match_files, ignore_index=True)

# Unieke tegenstanders ophalen
bayer_lever['opponent'] = bayer_lever.apply(
    lambda row: row['home_team']['home_team_name'] if row['away_team']['away_team_name'] == "Bayer Leverkusen"
    else row['away_team']['away_team_name'], axis=1)

# Voeg kolom toe voor thuis/uit informatie
bayer_lever['match_type'] = bayer_lever.apply(
    lambda row: 'Thuis' if row['home_team']['home_team_name'] == "Bayer Leverkusen" else 'Uit', axis=1)

# Dropdown voor tegenstander
opponent_selected = st.sidebar.selectbox("Selecteer een tegenstander", bayer_lever['opponent'].unique())

# Filter wedstrijden op geselecteerde tegenstander
filtered_matches = bayer_lever[bayer_lever['opponent'] == opponent_selected]

# Dropdown voor matchday
matchday_selected = st.sidebar.selectbox("Selecteer een matchday", filtered_matches['match_week'].unique())

# Filter wedstrijden op geselecteerde matchday
filtered_matches = filtered_matches[filtered_matches['match_week'] == matchday_selected]

# Dropdown voor thuis/uit selectie
home_or_away_selected = st.sidebar.selectbox("Was het een thuiswedstrijd of uitwedstrijd?", filtered_matches['match_type'].unique())

# Filter op thuis/uit selectie
filtered_matches = filtered_matches[filtered_matches['match_type'] == home_or_away_selected]

# Dropdown voor specifieke wedstrijd
match_selected = st.sidebar.selectbox("Selecteer een wedstrijd", filtered_matches['match_id'])

# Toon de geselecteerde wedstrijd
selected_match = filtered_matches[filtered_matches['match_id'] == match_selected].iloc[0]
st.title("Bayer Leverkusen Match Analyzer")
st.write(f"Geselecteerde wedstrijd: {selected_match['home_team']['home_team_name']} vs {selected_match['away_team']['away_team_name']} op {selected_match['match_date']} ({selected_match['match_type']})")

df_test = pd.read_csv('df_test.csv')

if match_selected:
    # Filter de dataset voor de geselecteerde wedstrijd
    selected_match_data = df_test[df_test['match_id'] == match_selected]


    
start_game = st.button("Start Wedstrijd")
stop_game = st.button("Stop Wedstrijd")


# Variabele om te controleren of de wedstrijd aan of uit is
game_running = False


# Als de startknop is ingedrukt, zet je game_running op True
if start_game:
    game_running = True


# Als de stopknop is ingedrukt, zet je game_running op False
if stop_game:
    game_running = False


import time
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

if game_running:
    match_minute_selected = 1
    # Lege lijsten voor xG-tijdslijn
    match_minutes = []
    xG_values = []
    goals_values = []

    # Voor het bijhouden van de xG per speler (voor de huidige minuut)
    player_xg = {}

    header_container = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        xg_chart_container = st.empty()
        pitch_chart_container = st.empty()
    with col2:
        table_container = st.empty()
        alternative_chart_container = st.empty()

    # Loop door de minuten (simulatie van live data)
    for match_minute_selected in range(1, 99):
        header_container.subheader(f"Minuut: {match_minute_selected}")

        # **Filter schoten tot de huidige minuut**
        df_minute = selected_match_data[selected_match_data['minute'] <= match_minute_selected]

        # **Update xG en Goals**
        match_minutes.append(match_minute_selected)
        xG_values.append(df_minute["Random Forest XG"].sum())
        goals_values.append(df_minute["goal"].sum())

        # **Update xG per speler voor deze minuut**
        player_xg.clear()  # Leegmaken van de xG voor elke minuut (geen cumulatie)

        for index, row in df_minute.iterrows():
            player = row["player"]
            xg = row["Random Forest XG"]
            if player in player_xg:
                player_xg[player] += xg
            else:
                player_xg[player] = xg

        # 1️⃣ **xG vs. Goals Grafiek**
        fig_xg, ax_xg = plt.subplots(figsize=(6, 4))
        ax_xg.plot(match_minutes, xG_values, label="Random Forest XG", marker="o", color="blue")
        ax_xg.plot(match_minutes, goals_values, label="Doelpunten", marker="s", color="red")
        ax_xg.set_xlabel("Minuut")
        ax_xg.set_ylabel("Waarde")
        ax_xg.set_title("xG en Werkelijke Goals")
        ax_xg.legend()

        plt.close(fig_xg)
        # 2️⃣ **Top 3 Spelers met de meeste xG tot nu toe**
        sorted_players = sorted(player_xg.items(), key=lambda x: x[1], reverse=True)

        top_3_players = sorted_players[:3]

        players = [player for player, _ in top_3_players]
        xg_values = [xg for _, xg in top_3_players]

        # Maak een horizontale barchart
        fig, ax = plt.subplots(figsize=(6, 4))
        hbars = ax.barh(players, xg_values, color='seagreen')

        # Voeg de xG-waarde toe als label aan de rechterkant van de balken
        ax.bar_label(hbars, fmt='%.2f', color='black')

        # Voeg de speler namen toe in het midden van de balken
        for i, bar in enumerate(hbars):
            ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                    players[i], ha='center', va='center', color='white', fontweight='bold')

        ax.set_yticklabels([])  # Geen labels op de y-as
        # Labels en titel
        ax.set_xlabel('xG (Expected Goals)')
        ax.set_ylabel('Speler')
        ax.set_title('Top 3 Spelers met de Meeste xG')

        plt.close(fig)

        # 3️⃣ **Schoten op het veld**
        pitch = VerticalPitch(half=True, goal_type='box', pitch_color='#22312b', line_color='#c7d5cc')
        fig_pitch, ax_pitch = pitch.draw(figsize=(6, 4))

        categories = {
            0: ('Blocked', '#ba4f45'),
            1: ('Goal', '#ad993c'),
            2: ('Off Target', '#3498db'),
            3: ('Post', '#9b59b6'),
            4: ('Saved', '#FF69B4'),
            5: ('Saved Off Target', '#2ecc71'),
            6: ('Saved To Post', '#f39c12'),
            7: ('Wayward', '#FFFF33'),
        }

        for cat, (label, color) in categories.items():
            df_cat = df_minute[df_minute["schot_specificatie"] == cat]
            pitch.scatter(df_cat.x, df_cat.y, c=color, marker='o', ax=ax_pitch, label=label)

        plt.legend(fontsize=8)
        plt.close(fig_pitch)

        # 4️⃣ **Alternatieve visualisatie (bv. Heatmap)**
        fig_alt, ax_alt = plt.subplots(figsize=(6, 4))

        ax_alt.set_facecolor('#22312b')
        ax_alt.set_xlim(32.5, 47.5)
        ax_alt.set_ylim(0, 4.5)

        ax_alt.plot([36, 36], [0, 2.67], color='#c7d5cc', linewidth=4)
        ax_alt.plot([44, 44], [0, 2.67], color='#c7d5cc', linewidth=4)
        ax_alt.plot([36, 44], [2.67, 2.67], color='#c7d5cc', linewidth=4)

        ax_alt.set_title('Shot Locations Near Goal', color='white')
        ax_alt.set_xticks([])
        ax_alt.set_yticks([])

        for cat, (label, color) in categories.items():
            df_cat = df_minute[df_minute["schot_specificatie"] == cat]
            ax_alt.scatter(df_cat.breedte_schot, df_cat.hoogte_schot, c=color, marker='o', label=label, alpha=0.7)

        ax_alt.legend(loc="upper right", fontsize=8)
        plt.close(fig_alt)

        # Update containers met figuren
        alternative_chart_container.pyplot(fig_alt)
        table_container.pyplot(fig)  # Update de tabel container
        xg_chart_container.pyplot(fig_xg)
        pitch_chart_container.pyplot(fig_pitch)

        # Herlaad de streamlit pagina (indien nodig)
        # st.experimental_rerun() # Uncomment dit als je wilt herladen

        # Wachten per minuut (vervang door herladen met streamlit)
        time.sleep(0.5)  # Dit kan de ervaring vertragen, probeer te experimenteren met snellere updates
 # Let op: Streamlit werkt meestal zonder sleep, tenzij je specifieke vertraging wilt

