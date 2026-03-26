# Pokemon Combat Simulator

Streamlit app that simulates a Pokemon battle using live data from the [PokeAPI](https://pokeapi.co/).

## Features

- Select two Pokemon and their moves to battle
- View stats comparison with interactive charts
- See battle log and HP over time visualization
- Type effectiveness calculated for dual-type defenders

## Deployed App

[Click here to open the app](https://pokemon-combat-simulator-group-3.streamlit.app/)

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
pokemon-combat-simulator/
├── app.py              # Main Streamlit dashboard
├── api.py              # PokeAPI calls and caching
├── battle.py           # Battle simulation logic
├── charts.py           # Plotly chart functions
├── requirements.txt    # Dependencies
├── pyproject.toml      # Project metadata
└── README.md
```

## Contributions

| Member | Responsibility |
|--------|---------------|
| **César González** | API integration — PokeAPI calls (`/pokemon/`, `/move/`, `/type/`), `@st.cache_data`, error handling |
| **Andrea Sabatés** | Pandas usage — stat comparison DataFrame con `.melt()`, battle log DataFrame, HP over time DataFrame |
| **Martí Solà** | Dashboard layout — Pokemon selection, sprites display, move selection widgets, `st.columns` layout |
| **Tina Jannasch** | Battle logic & charts — battle simulation, Plotly grouped bar chart, HP over time line chart |
| **Ricardo Velásquez** | Repo & deployment — `requirements.txt`, Streamlit deployment, repo structure and README |
