
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import folium_static
import numpy as np

st.title("Welcome to the EV Data Analysis Dashboard!")
st.subheader("Explore key trends and insights in the Indian EV market.")
st.markdown("⬅️Use the sidebar to dive in deeper.")
# Load data
@st.cache_data
def load_data():
  df1 = pd.read_csv('OperationalPC.csv')
  shapefile = gpd.read_file('in.shp')
  df2 = pd.read_csv('ev_cat_total.csv')
  df2W = pd.read_excel('ev_sales_2W_only.xlsx')
  df3W = pd.read_excel('ev_sales_3W_only.xlsx')
  dfLMV = pd.read_excel('ev_sales_LMV_only.xlsx')
  dfMMV = pd.read_excel('ev_sales_MMV_only.xlsx')
  df_makers = pd.read_csv('EV_MAKER_DATA.csv')
  df_vehicles = pd.read_csv('Vehicle_class_ev.csv')
  df_vehicles['Total Registration'] = df_vehicles['Total'] 
  return df1, shapefile, df2, df2W, df3W, dfLMV, dfMMV, df_makers, df_vehicles

df1, shapefile, df2, df2W, df3W, dfLMV, dfMMV, df_makers, df_vehicles = load_data()

#Setting the themes for the plots
sns.set_theme(style="dark", palette="rocket")
plt.style.use('dark_background')  

st.sidebar.write(" ")
selection = st.sidebar.radio(
    "Click on buttons below to analyse the following trend:",
    ["Home","Registration Trends", "Charging Infrastructure", "EV Makers Information"]
)

# Display content based on button clicks
def show_registration():
    st.subheader("Registration Trends")

    # Line Graph of Counts Over Time by Vehicle Type
    st.markdown("#### EV Registrations year on year by Vehicle Type(till 2023)")
    fig1, ax1 = plt.subplots(figsize=(20, 8))
    for column in df2.columns:
        if column != 'Date':
            ax1.plot(df2['Date'], df2[column], marker='.', linestyle='-', label=column)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Count')
    ax1.set_title('Line Graph of Counts Over Time by Vehicle Type')
    ax1.legend()
    ax1.grid(True)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

    # Total Registration by Vehicle Class(till2024)
    st.markdown("#### Total EV Registration by Vehicle Class(till 2024)") 
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Vehicle Class', y='Total', data=df_vehicles, orient='v')
    ax2.set_xlabel('Vehicle Class')
    ax2.set_ylabel('Total Registration(1 unit = 10 crore)')
    ax2.set_title('Total Registration by Vehicle Class')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig2)

def show_charging():
    st.subheader("Charging Infrastructure")

 # Choropleth map of Operational PCs by State
    st.markdown("#### State-wise Distribution of Operational Charging Stations")
    merged = shapefile.set_index('name').join(df1.set_index('State'))
    merged = merged.reset_index()
    merged = merged.set_geometry('geometry')
    merged.dropna(subset=['No. of Operational PCS'], inplace=True)

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=4.5)
    folium.Choropleth(
        geo_data=merged.__geo_interface__,
        name='No. of Operational PCs',
        data=merged,
        columns=['name', 'No. of Operational PCS'],
        key_on='feature.properties.name',
        fill_color='RdPu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Operational PCs by State'
    ).add_to(m)

    for _, row in merged.iterrows():
        state_name = row['name']
        pc_count = int(row['No. of Operational PCS'])
        geojson = row.geometry.__geo_interface__
        folium.GeoJson(
            geojson,
            tooltip=f'{state_name}: {pc_count}'
        ).add_to(m)

    folium_static(m)

    # Operational PC Barplots
    st.markdown("#### No. of Operational Charging Stations by State")

    operational_pc_bar_option = st.selectbox(
        "Select Bar Plot View:",
        ("All States", "Top 10 States"), key="opc_bar_select"
    )
    if operational_pc_bar_option == "All States":
        fig3, ax3 = plt.subplots(figsize=(15, 6))
        sns.barplot(x='State', y='No. of Operational PCS', data=df1, palette='deep', ax=ax3)
        ax3.set_xlabel('State')
        ax3.set_ylabel('No. of Operational PCs')
        ax3.set_title('Bar Chart of No. of Operational PCs by State')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig3)
    elif operational_pc_bar_option == "Top 10 States":
        st.markdown("##### Top 10 States by Operational Charging Stations")
        df1_top10 = df1.sort_values(by='No. of Operational PCS', ascending=False).head(10)
        fig4, ax4 = plt.subplots(figsize=(12, 6))
        for container in ax4.containers:
            ax4.bar_label(container, fmt='%d', label_type='edge', padding=3, color='white')
        sns.barplot(y='No. of Operational PCS', x='State', data=df1_top10, orient='v', palette='deep', ax=ax4)
        ax4.set_xlabel('State')
        ax4.set_ylabel('No. of Operational PCs')
        ax4.set_title('Top 10 States by No. of Operational PCs')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig4)


def show_makers():
    st.subheader("EV Makers Information")

    # EV Maker Locations Map
    st.markdown("#### Location of EV Makers")
    m_makers = folium.Map(location=[20.5937, 78.9629], zoom_start=4.5)
    for index, row in df_makers.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=row['EV Maker'],
            tooltip=row['EV Maker']
        ).add_to(m_makers)
    folium_static(m_makers)

    # Top EV Makers by Vehicle Category
    st.markdown("#### Top EV Makers by Vehicle Category")
    vehicle_category_maker_option = st.selectbox(
        "Select Vehicle Category:",
        ("2-Wheelers (2W)", "3-Wheelers (3W)", "Light Motor Vehicles (LMV)", "Medium Motor Vehicles (MMV)"), key="maker_cat_select"
    )

    if vehicle_category_maker_option == "2-Wheelers (2W)":
        st.markdown("##### Top 5 Total EV Makers (2W)")
        top5_2W_makers = df2W.sort_values(by='Total', ascending=False).head(5)
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Maker', y='Total', data=top5_2W_makers, palette='viridis', ax=ax5)
        ax5.set_ylabel('Total Number of EVs Sold')
        ax5.set_xlabel('Maker')
        plt.xticks(rotation=30, ha='right')
        ax5.set_title('Top 5 Total EV Makers (2W)')
        st.pyplot(fig5)

    elif vehicle_category_maker_option == "3-Wheelers (3W)":
        st.markdown("##### Top 5 Total EV Makers (3W)")
        top5_3W_makers = df3W.sort_values(by='Total', ascending=False).head(5)
        fig6, ax6 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Maker', y='Total', data=top5_3W_makers, palette='viridis', ax=ax6)
        ax6.set_ylabel('Total Number of EVs Sold')
        ax6.set_xlabel('Maker')
        plt.xticks(rotation=30, ha='right')
        ax6.set_title('Top 5 Total EV Makers (3W)')
        st.pyplot(fig6)

    elif vehicle_category_maker_option == "Light Motor Vehicles (LMV)":
        st.markdown("##### Top 5 Total EV Makers (LMV)")
        top5_lmv_makers = dfLMV.sort_values(by='Total', ascending=False).head(5)
        fig7, ax7 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Maker', y='Total', data=top5_lmv_makers, palette='viridis', ax=ax7)
        ax7.set_ylabel('Total Number of EVs Sold')
        ax7.set_xlabel('Maker')
        plt.xticks(rotation=30, ha='right')
        ax7.set_title('Top 5 Total EV Makers (LMV)')
        st.pyplot(fig7)

    elif vehicle_category_maker_option == "Medium Motor Vehicles (MMV)":
        st.markdown("##### Top 5 Total EV Makers (MMV)")
        top3_mmv_makers = dfMMV.sort_values(by='Total', ascending=False).head(5)
        fig8, ax8 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Maker', y='Total', data=top3_mmv_makers, palette='viridis', ax=ax8)
        ax8.set_ylabel('Total Number of EVs Sold')
        ax8.set_xlabel('Maker')
        plt.xticks(rotation=30, ha='right')
        ax8.set_title('Top 5 Total EV Makers (MMV)')
        st.pyplot(fig8)

# Now use `selection` to render different pages
if selection == "Home":
    st.write("Homepage")
    st.image("home.image.jpg", width=800)
elif selection == "Registration Trends":
    st.write("Showing registration trends...")
    show_registration()
elif selection == "Charging Infrastructure":
    st.write("Showing charging infrastructure...")
    show_charging()
elif selection == "EV Makers Information":
    st.write("Showing EV makers info...")
    show_makers()


