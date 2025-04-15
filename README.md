# Louisiana Labor Force Dashboard

This interactive [Streamlit](https://streamlit.io/) dashboard provides comprehensive insights into **Louisiana's labor market dynamics** by leveraging data from both the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) and the [Bureau of Labor Statistics (BLS)](https://www.bls.gov/). The dashboard supports both state-level and county-level (parish) analysis—offering detailed visualizations of unemployment, employment, and labor force trends across Louisiana.

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://la-laborforce-dashboard-d2c3ec8edfe6.herokuapp.com/)  
[![Heroku](https://img.shields.io/badge/Heroku-Deployed-blue)](https://la-laborforce-dashboard-d2c3ec8edfe6.herokuapp.com/)

---

## 📦 Features

- **State-Level Analysis**

  - Compare Louisiana with other states by viewing time-series line charts of unemployment rates and related metrics.
  - Interactive filters to select states, adjust the date range, and visualize comparative trends.
  - Choropleth maps that display state-level unemployment rates for a selected year.

- **County (Parish)-Level Analysis**

  - Visualize parish-level trends in key labor market metrics: _Unemployment Rate_, _Labor Force Size_, _Employment_, and _Unemployment_.
  - Time-series charts to track the evolution of metrics over time.
  - Interactive choropleth maps to explore regional disparities, with options to filter by parish and year.
  - Data tables available for download to support custom analysis.

- **Data Integration & Caching**
  - Efficient use of [Streamlit's caching](https://docs.streamlit.io/library/advanced-features/caching) to optimize data fetching from both FRED and BLS APIs.
  - Automated data merging through external scripts that compile national and county-level labor statistics.

---

## 🛠️ Technologies & Libraries

| Library/Tool  | Purpose                                         |
| ------------- | ----------------------------------------------- |
| **Streamlit** | Web app framework for interactive dashboards    |
| **pandas**    | Data manipulation and analysis                  |
| **plotly**    | Interactive charting and mapping visualizations |
| **requests**  | HTTP requests to query FRED & BLS APIs          |
| **fredapi**   | Fetch economic data from FRED                   |
| **Pillow**    | Display and process header images               |

---

## 📁 Project Structure

```
📁 Data-Science-Projects/
├── economics_dashboard_Heroku.py   # Main Streamlit dashboard script
├── Scrap BLS website.py            # Script to fetch and merge national and county-level labor data from the BLS API
├── Procfile                        # For Heroku deployment
├── merged_national_county_1990_2025.csv  # Generated dataset (created by crap_bls_website.py)
├── .gitignore                      # Ignore .pkl files
└── README.md                       # This README file

```

## 🚀 How to Run Locally

1. **Clone the Repository:**

   \`\`\`bash
   git clone https://github.com/Asif-Rasool/louisiana-labor-force-dashboard.git
   cd louisiana-labor-force-dashboard
   \`\`\`

2. **Install Dependencies:**

   Ensure you have Python 3.7 (or above) installed, then run:

   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set Up API Keys:**

   - **FRED API:**  
     Obtain your API key from [FRED](https://fred.stlouisfed.org/), and export it as an environment variable:

     \`\`\`bash
     export FRED_API_KEY=your_fred_api_key_here
     \`\`\`

   - **BLS API:**  
     Update the BLS API key in your configuration file (e.g., in \`.streamlit/secrets.toml\`) as required by the BLS scraping script.

4. **Generate/Update Data:**

   Run the data scraping script to fetch and merge BLS national and county-level labor data:

   \`\`\`bash
   python Scrap\ BLS\ website.py
   \`\`\`

   This will create or update the \`merged_national_county_1990_2025.csv\` file used by the dashboard.

5. **Launch the Dashboard:**

   Start the Streamlit app:

   \`\`\`bash
   streamlit run economics_dashboard_Heroku.py
   \`\`\`

---

## 🌐 Deployment Options

### Streamlit Cloud

- Connect your GitHub repository to [Streamlit Cloud](https://streamlit.io/cloud) and deploy your app with minimal configuration.

### Heroku

- Create a new Heroku app and deploy using the provided \`Procfile\`:

  \`\`\`bash
  heroku create louisiana-labor-dashboard
  git push heroku main
  \`\`\`

---

## 📊 Data Sources

- [**FRED (Federal Reserve Economic Data):**](https://fred.stlouisfed.org/) Provides state-level unemployment and related labor statistics.
- [**BLS (Bureau of Labor Statistics):**](https://www.bls.gov/) Supplies national and county-level data on labor force, employment, and unemployment metrics.

The data is dynamically fetched and merged for interactive visualization and analysis.

---

## 👨‍💻 Author

**Asif Rasool, Ph.D.**  
Research Economist, Southeastern Louisiana University  
📍 1514 Martens Drive, Hammond, LA 70401  
📞 985-549-3831  
✉️ [asif.rasool@southeastern.edu](mailto:asif.rasool@southeastern.edu)  
🌐 [Work Website](https://www.southeastern.edu/employee/asif-rasool/)  
🔗 [GitHub Repository](https://github.com/Asif-Rasool)

---

## ⏰ Last Updated

**April 11, 2025**

---

## ⭐️ Support & Contributions

If you find this project useful or have suggestions for improvements, please consider giving it a ⭐ and contributing to the project!
