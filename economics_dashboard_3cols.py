import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from fredapi import Fred

# --- PAGE CONFIG ---
st.set_page_config(page_title="U.S. State Unemployment Dashboard", layout="wide")

# --- Create three-column layout ---
col1, col2, col3 = st.columns([1, 6, 3])

# --- Centered header image using columns ---
image_path = "LaborDashboard.webp"  # Assuming the image is stored in the same folder as your script
with col2:
    st.image(image_path, use_container_width=True)

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

# Create three-column layout
col1, col2, col3 = st.columns([1, 6, 3])

# Show the About section in the right column (col3)
with col3:
    with st.expander("ℹ️ About", expanded=True):
        st.markdown("""
        This interactive dashboard provides insights into **labor market dynamics** across **Louisiana parishes**,
        including **Unemployment Rates**, **Labor Force Size**, **Employment**, and **Unemployment** trends.
        It is designed to support researchers, policy analysts, and local governments in exploring regional labor statistics.

        ---

        ### 🔍 **Key Capabilities**
        - Track **labor market trends** over time at the parish level
        - Compare metrics such as **employment**, **labor force**, and **unemployment** across parishes
        - Visualize data using **time series** and **choropleth maps**
        - Export filtered datasets for custom analysis and reporting

        ---

        ### 🧰 **Technologies & Tools**
        - **Streamlit** – Interactive interface framework
        - **pandas**, **numpy** – Data wrangling and manipulation
        - **plotly** – Interactive charts and maps
        - **Pillow** – Display image headers

        ---

        ### 📦 **Data Sources**
        - [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/)
        - [Bureau of Labor Statistics (BLS)](https://www.bls.gov/)

        ---

        **Asif Rasool, Ph.D.**
        Research Economist, Southeastern Louisiana University
        📍 1514 Martens Drive, Hammond, LA 70401
        📞 985-549-3831
        📧 [asif.rasool@southeastern.edu](mailto:asif.rasool@southeastern.edu)
        🌐 [Work Website](https://www.southeastern.edu/employee/asif-rasool/)
        🔗 [GitHub Repository](https://github.com/Asif-Rasool)

        _Last updated: April 2025_
        """)

# ========= SIDEBAR =========

# --- STATE LEVEL ANALYSIS SIDEBAR ---
st.sidebar.header("State Level Analysis")

# Dropdown multiselect with "Select All States" option.
states = list(STATE_SERIES_IDS.keys())
state_options = ["Select All States"] + states
selected_state_options = st.sidebar.multiselect(
    "Select states to compare:",
    options=state_options,
    default=["Louisiana", "Texas", "California"],
    key="state_select"
)
if "Select All States" in selected_state_options:
    states_selected = states
else:
    states_selected = selected_state_options

# Compute available date range from only the selected state series.
all_state_dates = [get_series(STATE_SERIES_IDS[s])["Date"] for s in states_selected if not get_series(STATE_SERIES_IDS[s]).empty]
if all_state_dates:
    common_start = max(series.min() for series in all_state_dates)
    common_end = min(series.max() for series in all_state_dates)
else:
    common_start, common_end = None, None

if common_start and common_end:
    start_date = st.sidebar.date_input("Start date", common_start, min_value=common_start, max_value=common_end, key="state_start_date")
    end_date = st.sidebar.date_input("End date", common_end, min_value=common_start, max_value=common_end, key="state_end_date")
else:
    start_date, end_date = None, None

# Insert gap between State Level and County Level sections in sidebar.
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# --- COUNTY LEVEL ANALYSIS SIDEBAR ---
st.sidebar.header("County Level Analysis")
# (County-level options will be set in the main content after loading county data.)

# ========= MAIN CONTENT =========

# --- STATE-LEVEL ANALYSIS ---
with col2:
    st.write('---')
    st.markdown("## State-Level Unemployment Analysis")

    # Load national series for US aggregate and state series.
    us_df = get_series("UNRATE").rename(columns={"Unemployment Rate": "United States"})
    comparison_df = us_df[["Date", "United States"]].copy()
    for state in states_selected:
        series_id = STATE_SERIES_IDS[state]
        state_data = get_series(series_id)
        if not state_data.empty:
            state_data = state_data.rename(columns={"Unemployment Rate": state})
            comparison_df = pd.merge(comparison_df, state_data, on="Date", how="left")

    # Filter the state-level data using the selected date range.
    if start_date and end_date:
        mask = (comparison_df["Date"] >= pd.to_datetime(start_date)) & (comparison_df["Date"] <= pd.to_datetime(end_date))
        comparison_df = comparison_df.loc[mask]

    # Build the state-level line chart.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=comparison_df["Date"],
        y=comparison_df["United States"],
        mode='lines',
        name='United States',
        line=dict(width=3, dash='dash')
    ))
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

    st.write('---')

    with st.expander("📄 Show Data Table & Download (State Level)"):
        st.dataframe(comparison_df)
        csv = comparison_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="state_unemployment.csv",
            mime="text/csv"
        )

    st.write('---')

    # --- STATE-LEVEL CHOROPLETH MAP WITH YEAR SLIDER ---
    if states_selected and common_start and common_end:
        selected_year_state = st.slider(
            "Select Year for State Map",
            min_value=common_start.year,
            max_value=common_end.year,
            value=common_start.year,
            step=1,
            key="state_year_slider"
        )
        # Filter state-level data for the selected year.
        df_year = comparison_df[comparison_df["Date"].dt.year == selected_year_state]

        state_map_data = []
        for state in states_selected:
            if state in df_year.columns and not df_year[state].dropna().empty:
                # Use the average unemployment rate for the state in the selected year.
                avg_rate = df_year[state].mean()
                state_map_data.append({"State": state, "Rate": round(avg_rate, 2)})

        if state_map_data:
            map_df = pd.DataFrame(state_map_data)
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
                    text=f"Unemployment Rate by State in {selected_year_state}",
                    x=0.5,
                    font=dict(size=20)
                ),
                margin=dict(l=20, r=20, t=60, b=20),
                height=600
            )
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.warning("No valid state data available for the selected year.")
    else:
        st.info("Please select a state to start data visualization.")

# --- COUNTY-LEVEL (PARISH) ANALYSIS ---
with col2:
    st.markdown("## County-Level (Parish) Unemployment Analysis")
    st.markdown("""
    This section shows a time series and a parish-level map for the **selected metric** 
    across Louisiana parishes. Use the sidebar to filter parishes, date range, and choose which metric to view.
    """)

    # Load county data
    @st.cache_data
    def load_county_data():
        try:
            df = pd.read_csv("merged_national_county_1990_2025.csv")
        except Exception as e:
            st.error(f"Failed to load county data: {e}")
            return pd.DataFrame()

        df.columns = df.columns.str.strip()

        if "Parish" in df.columns:
            df["Parish"] = df["Parish"].str.strip()
        else:
            st.error("The county data must contain a 'Parish' column.")
            return pd.DataFrame()

        if "Unemployment rate" in df.columns:
            df.rename(columns={"Unemployment rate": "Unemployment Rate"}, inplace=True)

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

        LA_PARISH_FIPS = {
            "Acadia": "22001", "Allen": "22003", "Ascension": "22005", "Assumption": "22007",
            "Avoyelles": "22009", "Beauregard": "22011", "Bienville": "22013", "Bossier": "22015",
            "Caddo": "22017", "Calcasieu": "22019", "Caldwell": "22021", "Cameron": "22023",
            "Catahoula": "22025", "Claiborne": "22027", "Concordia": "22029", "De Soto": "22031",
            "East Baton Rouge": "22033", "East Carroll": "22035", "East Feliciana": "22037",
            "Evangeline": "22039", "Franklin": "22041", "Grant": "22043", "Iberia": "22045",
            "Iberville": "22047", "Jackson": "22049", "Jefferson": "22051", "Jefferson Davis": "22053",
            "Lafayette": "22055", "Lafourche": "22057", "LaSalle": "22059", "Lincoln": "22061",
            "Livingston": "22063", "Madison": "22065", "Morehouse": "22067", "Natchitoches": "22069",
            "Orleans": "22071", "Ouachita": "22073", "Plaquemines": "22075", "Pointe Coupee": "22077",
            "Rapides": "22079", "Red River": "22081", "Richland": "22083", "Sabine": "22085",
            "St. Bernard": "22087", "St. Charles": "22089", "St. Helena": "22091", "St. James": "22093",
            "St. John the Baptist": "22095", "St. Landry": "22097", "St. Martin": "22099",
            "St. Mary": "22101", "St. Tammany": "22103", "Tangipahoa": "22105", "Tensas": "22107",
            "Terrebonne": "22109", "Union": "22111", "Vermilion": "22113", "Vernon": "22115",
            "Washington": "22117", "Webster": "22119", "West Baton Rouge": "22121",
            "West Carroll": "22123", "West Feliciana": "22125", "Winn": "22127"
        }
        df["fips"] = df["Parish"].map(LA_PARISH_FIPS)
        df = df.dropna(subset=["fips"])

        return df

    county_df = load_county_data()

    if county_df.empty:
        st.error("County-level data could not be loaded.")
    else:
        # === Sidebar Filters ===

        # === Metric Selection (in sidebar, single select) ===
        metric_options = ["Unemployment Rate", "Labor force size", "Employment", "Unemployment"]
        selected_metric = st.sidebar.selectbox(
            "Select a labor market metric:",
            options=metric_options,
            index=0
        )
        
        # Parishes
        parishes = sorted(county_df["Parish"].unique())
        county_options = ["Select All Parishes"] + parishes
        selected_county_options = st.sidebar.multiselect(
            "Select Parishes to Compare:",
            options=county_options,
            default=["St. Tammany", "Tangipahoa", "Livingston", "Washington", "St. Helena"],
            key="county_parishes_multiselect"
        )
        if "Select All Parishes" in selected_county_options:
            selected_parishes = parishes
        else:
            selected_parishes = selected_county_options

        # Date range
        county_common_start = county_df["Date"].min().date()
        county_common_end = county_df["Date"].max().date()
        county_start_date = st.sidebar.date_input(
            "County Start Date", value=county_common_start,
            min_value=county_common_start, max_value=county_common_end
        )
        county_end_date = st.sidebar.date_input(
            "County End Date", value=county_common_end,
            min_value=county_common_start, max_value=county_common_end
        )

        # === Time-Series Chart ===
        st.markdown("### 📈 Time-Series Chart")

        filtered_line_df = county_df[ 
            (county_df["Parish"].isin(selected_parishes)) & 
            (county_df["Date"] >= pd.to_datetime(county_start_date)) & 
            (county_df["Date"] <= pd.to_datetime(county_end_date))
        ]

        if not filtered_line_df.empty:
            fig_line = go.Figure()
            for parish in selected_parishes:
                df_parish = filtered_line_df[filtered_line_df["Parish"] == parish]
                if selected_metric in df_parish.columns:
                    fig_line.add_trace(go.Scatter(
                        x=df_parish["Date"],
                        y=df_parish[selected_metric],
                        mode='lines',
                        name=parish
                    ))
            fig_line.update_layout(
                title=f"{selected_metric} Over Time",
                xaxis_title="Date",
                yaxis_title=selected_metric,
                hovermode="x unified",
                template="plotly_white",
                height=500,
                legend=dict(orientation="h", y=-0.3)
            )
            st.plotly_chart(fig_line, use_container_width=True)

            with st.expander("📄 Show Data Table & Download"):
                st.dataframe(filtered_line_df[["Date", "Parish", selected_metric]])
                csv = filtered_line_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "parish_labor_metrics.csv", "text/csv")
        else:
            st.warning("No data available for selected filters.")

        st.write('---')

        # === Choropleth Map ===
        st.markdown("### 🗺️ Parish-Level Choropleth Map")

        selected_year = st.slider(
            "Select Year for Map",
            min_value=int(county_df["year"].min()),
            max_value=int(county_df["year"].max()),
            value=int(county_df["year"].min()),
            step=1
        )

        filtered_map_df = county_df[ 
            (county_df["year"] == selected_year) & 
            (county_df["Parish"].isin(selected_parishes))
        ]

        @st.cache_data
        def load_geojson():
            url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
            response = requests.get(url)
            geojson = response.json()
            geojson["features"] = [
                f for f in geojson["features"] if f["id"].startswith("22")
            ]
            return geojson

        if not filtered_map_df.empty:
            geojson_data = load_geojson()
            fig_map = px.choropleth(
                filtered_map_df,
                geojson=geojson_data,
                locations="fips",
                color=selected_metric,
                color_continuous_scale="Viridis",
                range_color=(
                    filtered_map_df[selected_metric].min(),
                    filtered_map_df[selected_metric].max()
                ),
                scope="usa",
                labels={selected_metric: selected_metric},
                title=f"{selected_metric} by Parish in {selected_year}",
                hover_name="Parish"
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                template="plotly_dark",
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No parish data available for the selected year.")


