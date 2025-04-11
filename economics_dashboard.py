import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from fredapi import Fred

# --- PAGE CONFIG ---
st.set_page_config(page_title="U.S. State Unemployment Dashboard", layout="wide")
st.title("U.S. Unemployment Rate by State")

st.markdown("""
This dashboard visualizes the **historical unemployment rate** across **U.S. states**, using official data from the **Federal Reserve Economic Database (FRED)**.
""")

# --- API ---
API_KEY = st.secrets["FRED"]["api_key"]
fred = Fred(api_key=API_KEY)

# --- STATE SERIES MAPPING ---
STATE_SERIES_IDS = {
    "Alabama": "ALUR", "Alaska": "AKUR", "Arizona": "AZUR", "Arkansas": "ARUR",
    "California": "CAUR", "Colorado": "COUR", "Connecticut": "CTUR", "Delaware": "DEUR",
    "District of Columbia": "DCUR", "Florida": "FLUR", "Georgia": "GAUR", "Hawaii": "HIUR",
    "Idaho": "IDUR", "Illinois": "ILUR", "Indiana": "INUR", "Iowa": "IAUR", "Kansas": "KSUR",
    "Kentucky": "KYUR", "Louisiana": "LAUR", "Maine": "MEUR", "Maryland": "MDUR",
    "Massachusetts": "MAUR", "Michigan": "MIUR", "Minnesota": "MNUR", "Mississippi": "MSUR",
    "Missouri": "MOUR", "Montana": "MTUR", "Nebraska": "NEUR", "Nevada": "NVUR",
    "New Hampshire": "NHUR", "New Jersey": "NJUR", "New Mexico": "NMUR", "New York": "NYUR",
    "North Carolina": "NCUR", "North Dakota": "NDUR", "Ohio": "OHUR", "Oklahoma": "OKUR",
    "Oregon": "ORUR", "Pennsylvania": "PAUR", "Rhode Island": "RIUR", "South Carolina": "SCUR",
    "South Dakota": "SDUR", "Tennessee": "TNUR", "Texas": "TXUR", "Utah": "UTUR",
    "Vermont": "VTUR", "Virginia": "VAUR", "Washington": "WAUR", "West Virginia": "WVUR",
    "Wisconsin": "WIUR", "Wyoming": "WYUR"
}

# --- FRED FETCH FUNCTION ---
@st.cache_data
def get_series(series_id):
    try:
        data = fred.get_series(series_id)
        df = pd.DataFrame(data).reset_index()
        df.columns = ["Date", "Unemployment Rate"]
        return df
    except Exception as e:
        st.error(f"Failed to fetch data for series {series_id}: {e}")
        return pd.DataFrame()

# --- STATE SELECTION ---
st.sidebar.header("Filter")
states_selected = st.sidebar.multiselect(
    "Select states to compare:",
    list(STATE_SERIES_IDS.keys()),
    default=["Louisiana", "Texas", "California"]
)

# --- Load Data for State-Level Analysis ---
us_df = get_series("UNRATE").rename(columns={"Unemployment Rate": "United States"})
comparison_df = us_df[["Date", "United States"]].copy()

for state in states_selected:
    series_id = STATE_SERIES_IDS[state]
    state_data = get_series(series_id)
    if not state_data.empty:
        state_data = state_data.rename(columns={"Unemployment Rate": state})
        comparison_df = pd.merge(comparison_df, state_data, on="Date", how="left")

# --- Calculate Common Date Range ---
all_dates = [us_df["Date"]] + [get_series(STATE_SERIES_IDS[s])["Date"] for s in states_selected]
common_start = max(df.min() for df in all_dates)
common_end = min(df.max() for df in all_dates)

start_date = st.sidebar.date_input("Start date", common_start, min_value=common_start, max_value=common_end)
end_date = st.sidebar.date_input("End date", common_end, min_value=common_start, max_value=common_end)

mask = (comparison_df["Date"] >= pd.to_datetime(start_date)) & (comparison_df["Date"] <= pd.to_datetime(end_date))
comparison_df = comparison_df.loc[mask]

# --- PLOTLY STATE-LEVEL CHART ---
fig = go.Figure()

# U.S. line
fig.add_trace(go.Scatter(
    x=comparison_df["Date"],
    y=comparison_df["United States"],
    mode='lines',
    name='United States',
    line=dict(width=3, dash='dash')
))

# State lines
for state in states_selected:
    fig.add_trace(go.Scatter(
        x=comparison_df["Date"],
        y=comparison_df[state],
        mode='lines',
        name=state
    ))

fig.update_layout(
    template="plotly_white",
    title="Unemployment Rate by State",
    xaxis_title="Date",
    yaxis_title="Unemployment Rate (%)",
    hovermode="x unified",
    height=500,
    legend=dict(orientation="h", y=-0.2)
)

st.plotly_chart(fig, use_container_width=True)

# --- TABLE + DOWNLOAD ---
with st.expander("📄 Show Data Table & Download"):
    st.dataframe(comparison_df)
    csv = comparison_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="state_unemployment.csv",
        mime="text/csv"
    )

# --- STATE-LEVEL MAP SECTION ---
if states_selected:
    # Get the latest unemployment rate for selected states
    latest_values = []
    latest_date = comparison_df["Date"].max()

    for state in states_selected:
        try:
            latest_rate = comparison_df.loc[comparison_df["Date"] == latest_date, state].values[0]
            latest_values.append({
                "State": state,
                "Rate": round(latest_rate, 2)
            })
        except:
            continue

    # Create DataFrame for the map
    map_df = pd.DataFrame(latest_values)
    
    # Convert full state names to USPS codes for Plotly
    state_abbr = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
        "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
        "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
        "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
        "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
        "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }
    map_df["State Code"] = map_df["State"].map(state_abbr)

    # Build modern state-level map
    map_fig = go.Figure(data=go.Choropleth(
        locations=map_df["State Code"],
        z=map_df["Rate"],
        locationmode='USA-states',
        colorscale="Blues",
        autocolorscale=False,
        colorbar=dict(title="Rate (%)", ticksuffix="%"),
        marker_line_color="white",
        marker_line_width=0.5,
        text=map_df.apply(lambda row: f"{row['State']}<br>{row['Rate']}%", axis=1),
        hoverinfo="text"
    ))

    map_fig.update_layout(
        template="plotly_dark",
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgba(255, 255, 255, 0.2)'
        ),
        title=dict(
            text=f"Unemployment Rate by State – {latest_date.date()}",
            x=0.5,
            font=dict(size=20)
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=600
    )

    st.plotly_chart(map_fig, use_container_width=True)
else:
    st.info("Please select a state to start data visualization.")

# --- COUNTY-LEVEL ANALYSIS ---
st.markdown("## County-Level (Parish) Unemployment Analysis")
st.markdown("""
This interactive map displays the unemployment rate by parish.
Use the slider below to select a year between 1990 and 2025.
""")

@st.cache_data
def load_county_data():
    try:
        # Load your cleaned Louisiana parish-level data.
        df = pd.read_csv("merged_national_county_1990_2025.csv")
    except Exception as e:
        st.error(f"Failed to load county data: {e}")
        return pd.DataFrame()
    
    # Strip extra whitespace from column names.
    df.columns = df.columns.str.strip()
    
    # Ensure the 'Parish' column is stripped of extra whitespace.
    if "Parish" in df.columns:
        df["Parish"] = df["Parish"].str.strip()
    else:
        st.error("The county data must contain a 'Parish' column.")
        return pd.DataFrame()
    
    # Rename "Unemployment rate" to "Unemployment Rate" for consistency.
    if "Unemployment rate" in df.columns:
        df.rename(columns={"Unemployment rate": "Unemployment Rate"}, inplace=True)
    
    # Process the 'Date' column.
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce', infer_datetime_format=True)
        if df["Date"].isnull().all():
            st.error("The 'Date' column exists but none of the dates could be parsed.")
            return pd.DataFrame()
        df["year"] = df["Date"].dt.year
    elif "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors='coerce')
    else:
        st.error("The county data must contain either a 'Date' or 'year' column.")
        return pd.DataFrame()
    
    # Mapping from Louisiana parish names to FIPS codes.
    LA_PARISH_FIPS = {
        "Acadia": "22001",
        "Allen": "22003",
        "Ascension": "22005",
        "Assumption": "22007",
        "Avoyelles": "22009",
        "Beauregard": "22011",
        "Bienville": "22013",
        "Bossier": "22015",
        "Caddo": "22017",
        "Calcasieu": "22019",
        "Caldwell": "22021",
        "Cameron": "22023",
        "Catahoula": "22025",
        "Claiborne": "22027",
        "Concordia": "22029",
        "De Soto": "22031",
        "East Baton Rouge": "22033",
        "East Carroll": "22035",
        "East Feliciana": "22037",
        "Evangeline": "22039",
        "Franklin": "22041",
        "Grant": "22043",
        "Iberia": "22045",
        "Iberville": "22047",
        "Jackson": "22049",
        "Jefferson": "22051",
        "Jefferson Davis": "22053",
        "Lafayette": "22055",
        "Lafourche": "22057",
        "LaSalle": "22059",
        "Lincoln": "22061",
        "Livingston": "22063",
        "Madison": "22065",
        "Morehouse": "22067",
        "Natchitoches": "22069",
        "Orleans": "22071",
        "Ouachita": "22073",
        "Plaquemines": "22075",
        "Pointe Coupee": "22077",
        "Rapides": "22079",
        "Red River": "22081",
        "Richland": "22083",
        "Sabine": "22085",
        "St. Bernard": "22087",
        "St. Charles": "22089",
        "St. Helena": "22091",
        "St. James": "22093",
        "St. John the Baptist": "22095",
        "St. Landry": "22097",
        "St. Martin": "22099",
        "St. Mary": "22101",
        "St. Tammany": "22103",
        "Tangipahoa": "22105",
        "Tensas": "22107",
        "Terrebonne": "22109",
        "Union": "22111",
        "Vermilion": "22113",
        "Vernon": "22115",
        "Washington": "22117",
        "Webster": "22119",
        "West Baton Rouge": "22121",
        "West Carroll": "22123",
        "West Feliciana": "22125",
        "Winn": "22127"
    }
    # Map Parish names to FIPS codes and drop rows where mapping fails.
    df["fips"] = df["Parish"].map(LA_PARISH_FIPS)
    df = df.dropna(subset=["fips"])
    
    return df

# In your county-level section of the app:
county_df = load_county_data()

if not county_df.empty:
    min_year_county = int(county_df["year"].min())
    max_year_county = int(county_df["year"].max())
    
    selected_year_county = st.slider(
        "Select Year for Parish Data",
        min_value=min_year_county,
        max_value=max_year_county,
        value=min_year_county,
        step=1,
        key="county_year_slider"
    )
    
    filtered_county_df = county_df[county_df["year"] == selected_year_county]
    
    if filtered_county_df.empty:
        st.warning("No parish data available for the selected year.")
    else:
        @st.cache_data
        def load_geojson():
            url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
            response = requests.get(url)
            geojson = response.json()
            return geojson

        counties_geojson = load_geojson()

        fig_county = px.choropleth(
            filtered_county_df,
            geojson=counties_geojson,
            locations='fips',               # Use the mapped FIPS codes
            color='Unemployment Rate',      # Numeric column with unemployment rates
            color_continuous_scale="Viridis",
            range_color=(filtered_county_df["Unemployment Rate"].min(), 
                         filtered_county_df["Unemployment Rate"].max()),
            scope="usa",
            labels={'Unemployment Rate': 'Unemployment Rate (%)'}
        )

        fig_county.update_geos(fitbounds="locations", visible=False)
        fig_county.update_layout(
            title_text=f"Unemployment Rate by Parish in {selected_year_county}",
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )

        st.plotly_chart(fig_county, use_container_width=True)
else:
    st.error("County-level data could not be loaded.")

