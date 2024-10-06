import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from streamlit_folium import st_folium
import plotly.graph_objects as go



# Set the page configuration
st.set_page_config(
    page_title="BMW FTA Scope",
    page_icon=":car:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)
# background-image: url("https://raw.atc-github.azure.cloud.bmw/q657525/FTA/main/BMW_Group_Investor_Relations_Presentation_Jan_2024_Update_2_Auszug_24-03-14_0846(1).png?token=GHSAT0AAAAAAAADKZVD2QBJRAF6HRICEUM2ZX3UHPQ");

# Add a blue-ish background with a world map image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] > .main {
background-image: url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fd1e00ek4ebabms.cloudfront.net%2Fproduction%2F17b7e4b3-5e4f-40c0-8b00-8ca7034d3af1.jpg&f=1&nofb=1&ipt=4d9e740341e6c77a34ccc3a707e26f0ebb8b25bcaa24dbe3fc8540ed74e1b320&ipo=images");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-color: #1a237e;
color: #ffffff;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Title and description for the web app
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <h1 style="font-size: 60px; font-weight: bold; color: #ffffff; text-shadow: 4px 4px 0 #1a237e, 6px 6px 0 rgba(0, 0, 0, 0.5); font-family: 'Arial Black', sans-serif;">FTA DATA LAKE</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Set the folder path containing the FTA data
fta_data_folder = "FTA_data"

# Get the list of unique Excel file names (without the .xlsx extension and in uppercase, excluding temporary files)
excel_files = [os.path.splitext(f)[0].upper() for f in os.listdir(fta_data_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
excel_files = list(set(excel_files))

# Create the main options for the user
st.markdown("## Select Suitable Operation")
view_options = ["General Overview", "Country Specific"]
selected_view = st.radio("Select View", view_options, key="selected_view_radio")

# Create the sidebar based on the selected view
with st.sidebar:
    if selected_view == "General Overview":
        # Create a selectbox for the user to select the export country
        st.markdown("## Select Export Country")
        source_country = st.selectbox(
            "Export Country",  # Added a meaningful label for accessibility
            [""] + excel_files,
            key="source_country_selectbox",
            label_visibility="collapsed"
        )

        # Check if a source country is selected
        if source_country:
            # Get the list of sheets in the selected Excel file
            excel_file = os.path.join(fta_data_folder, f"{source_country.lower()}.xlsx")
            if os.path.exists(excel_file):
                df = pd.read_excel(excel_file, sheet_name=None)
                sheet_names = list(df.keys())

                # Skip the first 2 sheets
                sheet_names = sheet_names[2:]

                # Create a selectbox for the user to select the sheet in the sidebar
                st.markdown("## Select Import Region")
                selected_sheet = st.selectbox(
                    "Import Region",  # Added a meaningful label for accessibility
                    [""] + sheet_names,
                    key="selected_sheet_selectbox",
                    label_visibility="collapsed"
                )
            else:
                st.warning(f"No Excel file found for {source_country.upper()}.")
        else:
            st.warning("Please select an Export (Production Country).")

    elif selected_view == "Country Specific":
        # Create a dropdown for selecting the Export Country
        st.markdown("## Select Export Country")
        export_country = st.selectbox(
            "Export Country",  # Label for accessibility
            [""] + excel_files,
            key="export_country_selectbox",
            label_visibility="collapsed"
        )

        # If an export country is selected, show the Import Country dropdown
        if export_country:
            # Load the selected export country Excel file
            excel_file = os.path.join(fta_data_folder, f"{export_country.lower()}.xlsx")
            if os.path.exists(excel_file):
                df = pd.read_excel(excel_file, sheet_name=None)
                
                # Ensure that the selected import country is properly defined
                unique_country_names = set()  # Use a set to automatically handle uniqueness

                # Iterate through the sheets to collect unique import country names
                sheet_names = list(df.keys())
                for sheet_name in sheet_names[2:]:  # Skip first 2 sheets
                    sheet_df = df[sheet_name]
                    if 'Country/Region' in sheet_df.columns:
                        unique_country_names.update([str(x) for x in sheet_df['Country/Region'].unique()])

                # Convert the set back to a sorted list for displaying in the dropdown
                unique_country_names = sorted(list(unique_country_names))

                # Create a dropdown for selecting the Import Country
                st.markdown("## Select Import Country")
                selected_import_country = st.selectbox(
                    "Import Country",  # Label for accessibility
                    [""] + unique_country_names,
                    key="selected_import_country_selectbox",
                    label_visibility="collapsed"
                )

                # If an import country is selected, proceed with processing the data
                if selected_import_country:
                    try:
                        # Process and display data for the selected import country
                        country_specific_dfs = []  # List to store rows for the selected import country

                        # Iterate through the sheets and filter the data for the selected import country
                        for sheet_name in sheet_names[2:]:  # Skip the first two sheets
                            sheet_df = df[sheet_name]
                            if 'Country/Region' in sheet_df.columns:
                                # Get the rows for the selected import country
                                start_idx = sheet_df[sheet_df['Country/Region'] == selected_import_country].index
                                
                                if not start_idx.empty:
                                    start_idx = start_idx[0]  # First index of the selected country

                                    # Iterate through rows from start_idx onwards
                                    for idx in range(start_idx, len(sheet_df)):
                                        if pd.notnull(sheet_df.loc[idx, 'Country/Region']) and sheet_df.loc[idx, 'Country/Region'] != selected_import_country:
                                            break  # Stop when a new country appears
                                        country_specific_dfs.append(sheet_df.iloc[idx])

                        # Convert the list of rows into a DataFrame and display it
                        if country_specific_dfs:
                            combined_df = pd.DataFrame(country_specific_dfs)
                            
                        else:
                            st.warning(f"No data found for {selected_import_country}.")

                    except Exception as e:
                        st.error(f"Error processing data for {selected_import_country}: {e}")

            else:
                st.warning(f"No Excel file found for {export_country.upper()}.")
        else:
            st.warning("Please select an Export (Production Country).")



if selected_view == "General Overview":

    if source_country and selected_sheet:
        try:
            sheet_df = df[selected_sheet]
        
            # Create separate dataframes for each country/region
            country_dfs = {}
            current_country = None
            for _, row in sheet_df.iterrows():
                country_region = row['Country/Region']
                if pd.notnull(country_region):
                    current_country = country_region
                
                if current_country not in country_dfs:
                    country_dfs[current_country] = pd.DataFrame(columns=['Vehicle Type', 'Tariff Type', 'Tariff Min.', 'Tariff Max.', 'Exceptions/Notes', 'Tariff Reduction Years', 'Reduction Rate%', 'EiF'])
                
                # Fill in the missing Vehicle Type values
                if pd.isnull(row['Vehicle Type']):
                    row['Vehicle Type'] = country_dfs[current_country]['Vehicle Type'].iloc[-1] if len(country_dfs[current_country]) > 0 else ''
                
                country_dfs[current_country] = pd.concat([country_dfs[current_country], pd.DataFrame({
                    'Vehicle Type': [row['Vehicle Type']],
                    'Tariff Type': [row['Tariff Type']],
                    'Tariff Min.': [row['Tariff Rate']],
                    'Tariff Max.': [row['Unnamed: 4']],
                    'Exceptions/Notes': [row['Exceptions/Notes']],
                    'Tariff Reduction Years': [row['Tariff Reduction Years']],
                    'Reduction Rate%': [row['Reduction Rate%']],
                    'EiF': [row['EiF']]
                })], ignore_index=True)
            # Assuming 'country_dfs' is ready and contains valid DataFrame for each country.
                
            # Assuming 'country_dfs' is ready and contains valid DataFrame for each country.
            print(country_dfs)
            # Display the graphs
            # Check if there is an 'LC' column in the DataFrame
            lc_column = None
            for col in sheet_df.columns:
                if str(col).startswith("LC"):
                    lc_column = col
                    break

                # Display the LC details in a small box on the right side
            if lc_column is not None:
                st.markdown(
                    f"""
                    <div style="background-color: orange; color: #003366; padding:0px; border-radius: 20px; box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25); margin-top: 20px; width: 300px; float: right;">
                        <h2 style="text-align: center; font-size: 18px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);">{lc_column}</h2>
                    
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            for country, df in country_dfs.items():
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <h1 style="font-size: 40px; font-weight: bold; color: #ffffff; text-shadow: 4px 4px 0 #1a237e, 6px 6px 0 rgba(0, 0, 0, 0.5); font-family: 'Arial Black', sans-serif;">{country.upper()}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                try:
                    # Filter the data
                    filtered_data = df.copy()

                    # Replace NaN values in 'Tariff Min.' and 'Tariff Max.' with reasonable defaults (like 0 or any other value that makes sense for your use case)
                    filtered_data['Tariff Min.'] = filtered_data['Tariff Min.'].fillna(0)
                    filtered_data['Tariff Max.'] = filtered_data['Tariff Max.'].fillna(0)

                    # Create a categorical type for sorting
                    vehicle_order = ['Others', 'BEV', 'PHEV', 'HEV', 'ICE']
                    filtered_data['Vehicle Type'] = pd.Categorical(filtered_data['Vehicle Type'], categories=vehicle_order, ordered=True)

                    # Sort the DataFrame based on the custom order
                    filtered_data = filtered_data.sort_values('Vehicle Type')

                    # Prepare the Plotly figure
                    fig = go.Figure()

                    # Define the width of the bars
                    bar_width = 0.3  # Width of each bar

                    # Flags to add legend entries once
                    mfn_legend_added = False
                    fta_legend_added = False

                
                    
                    # Loop through the vehicle types
                    for vehicle_type in vehicle_order:
                        vehicle_data = filtered_data[filtered_data['Vehicle Type'] == vehicle_type]

                        # Calculate MFN tariffs
                        mfn_row = vehicle_data[vehicle_data['Tariff Type'] == 'MFN']
                        if not mfn_row.empty:
                            mfn_min = mfn_row['Tariff Min.'].values[0]
                            mfn_max = mfn_row['Tariff Max.'].values[0]
                            mfn_exceptions = mfn_row['Exceptions/Notes'].values[0] or 'None'
                            mfn_reduction_rate = mfn_row['Reduction Rate%'].values[0] or 'N/A'
                            mfn_eff_date = mfn_row['EiF'].values[0] or 'N/A'

                            if mfn_min == 0 and mfn_max == 0:
                                mfn_mean = 0
                                mfn_error = 0
                                mfn_text = "<b><span style='color:blue;font-size:16px'>MFN = 0</span></b>"
                            else:
                                mfn_mean = (mfn_min + mfn_max) / 2  # Calculate the mean
                                mfn_error = (mfn_max - mfn_min) / 2  # Error is half the range
                                mfn_text = f"MFN: {mfn_min} - {mfn_max}"

                            fig.add_trace(go.Bar(
                                y=[vehicle_type],
                                x=[mfn_mean],
                                name='MFN Tariff' if not mfn_legend_added else None,  # Add legend only once
                                orientation='h',
                                width=bar_width,  # Set bar width
                                offset=-bar_width/2,  # Shift to the left for MFN
                                marker=dict(color='rgba(31, 119, 180, 0.5)'),  # Adjusted opacity for MFN
                                error_x=dict(
                                    type='data',
                                    array=[mfn_error],
                                    arrayminus=[mfn_error],
                                    width=0,
                                    color='rgba(31, 119, 180, 1)',  # Color of the error bars for MFN
                                    thickness=36
                                ),
                                text=[mfn_text],
                                textposition='outside',
                                hovertemplate=(
                                    f"<b>Vehicle Type: {vehicle_type}</b><br>" +
                                    f"{mfn_text}<br>" +
                                    f"Exceptions/Notes: {mfn_exceptions}<br>" +
                                    f"Reduction Rate: {mfn_reduction_rate}%<br>" +
                                    f"Effective Date (EiF): {mfn_eff_date}"
                                ),
                                showlegend=not mfn_legend_added  # Show legend only once for MFN
                            ))
                            mfn_legend_added = True  # Mark MFN legend as added

                        # Calculate FTA tariffs
                        fta_row = vehicle_data[vehicle_data['Tariff Type'] == 'FTA']
                        if not fta_row.empty:
                            fta_min = fta_row['Tariff Min.'].values[0] if pd.notna(fta_row['Tariff Min.'].values[0]) else 0
                            fta_max = fta_row['Tariff Max.'].values[0]
                            fta_exceptions = fta_row['Exceptions/Notes'].values[0] or 'None'
                            fta_reduction_rate = fta_row['Reduction Rate%'].values[0] or 'N/A'
                            fta_eff_date = fta_row['EiF'].values[0] or 'N/A'

                            if fta_min == 0 and fta_max == 0:
                                fta_mean = 0
                                fta_error = 0
                                fta_text = "<b><span style='color:green;font-size:16px'>FTA = 0</span></b>"
                            elif fta_max == 0:
                                fta_mean = fta_min
                                fta_error = 0
                                fta_text = "<b><span style='color:orange;font-size:16px'>FTA = Out of Scope</span></b>"
                            else:
                                fta_mean = fta_max  # Using max for FTA
                                fta_error = (fta_max - fta_min) / 2  # Error is half the range
                                fta_text = f"FTA: {fta_min} - {fta_max}"

                            fig.add_trace(go.Bar(
                                y=[vehicle_type],
                                x=[fta_mean],
                                name='FTA Tariff' if not fta_legend_added else None,  # Add legend only once
                                orientation='h',
                                width=bar_width,  # Set bar width
                                offset=bar_width/2,  # Shift to the right for FTA
                                marker=dict(color='rgba(44, 160, 44, 0.8)'),  # Adjusted opacity for FTA
                                error_x=dict(
                                    type='data',
                                    array=[fta_error],
                                    arrayminus=[fta_error],
                                    width=0,
                                    color='rgba(44, 160, 44, 1)',  # Color of the error bars for FTA
                                    thickness=36
                                ),
                                text=[fta_text],
                                textposition='outside',
                                hovertemplate=(
                                    f"<b>Vehicle Type: {vehicle_type}</b><br>" +
                                    f"{fta_text}<br>" +
                                    f"Exceptions/Notes: {fta_exceptions}<br>" +
                                    f"Reduction Rate: {fta_reduction_rate}%<br>" +
                                    f"Effective Date (EiF): {fta_eff_date}"
                                ),
                                showlegend=not fta_legend_added  # Show legend only once for FTA
                            ))
                            fta_legend_added = True  # Mark FTA legend as added

                    # Customize the layout for clarity
                    fig.update_layout(
                        barmode='overlay',  # Overlay MFN and FTA bars
                        
                        title={
                                'text': f"Tariff Overview (MFN vs FTA) for {country}",
                                'x': 0.5,
                                'xanchor': 'center' ,
                                'font': {
                                        'size': 32,
                                        'family': 'Arial, sans-serif',
                                        'color': 'black',
                                        'weight': 'bold'
                                    }
                            },
                        xaxis_title="Tariff (%)",
                        yaxis_title="Vehicle Type",
                        legend_title="Tariff Type",
                        legend={
                                'x': -0.08,  # Move the legend to the top left corner
                                'y': 1.15,
                                'bgcolor': 'rgba(255, 255, 255, 0.8)',  # Add a semi-transparent background to the legend
                                'bordercolor': 'rgba(200, 200, 200, 0.5)',  # Add a border to the legend
                                'borderwidth': 1
                            },
                        height=800,
                        width=1200,
                        bargap=0.4,
                        template='plotly_white',
                        
                        # Transparent background
                        plot_bgcolor='rgba(255, 255, 255, 0.2)',  # Transparent plot background
                        paper_bgcolor='rgba(255, 255, 255, 0.5)',  # Transparent overall background
                        # Center-align the plot and background
                        margin=dict(l=100, r=100, t=100, b=100),
                        autosize=False,
                                
                        # Customizing the x-axis
                        xaxis=dict(
                            tickfont=dict(
                                size=14,
                                color='black',
                                family='Arial, sans-serif',
                                weight='bold'
                            ),
                            title_font=dict(size=16, family='Arial, sans-serif', color='black', weight='bold'),  # Bold x-axis label
                            showgrid=True,
                            gridcolor='rgba(200, 200, 200, 0.8)',  # Increase gridline opacity for better visibility
                            zeroline=True,
                            zerolinecolor='rgba(200, 200, 200, 0.8)',  # Increase zero-line opacity for better visibility
                            tickformat='.2f'  # Format x-axis ticks with 2 decimal places
                        ),
                        
                        # Customizing the y-axis
                        yaxis=dict(
                            tickfont=dict(
                                size=14,
                                color='black',
                                family='Arial, sans-serif',
                                weight='bold'
                            ),
                            categoryorder='array',
                            categoryarray=vehicle_order,
                            title_font=dict(size=16, family='Arial, sans-serif', color='black', weight='bold'),  # Bold y-axis label
                            showgrid=True,
                            gridcolor='rgba(200, 200, 200, 0.8)',  # Increase gridline opacity for better visibility
                            zeroline=True,
                            zerolinecolor='rgba(200, 200, 200, 0.8)'  # Increase zero-line opacity for better visibility
                        )
                    )
                    

                    # Display the Plotly chart in Streamlit
                    st.plotly_chart(fig, use_container_width=True)

                
                except Exception as e:
                    st.warning(f"Error processing data for {country.upper()}: {str(e)}. Skipping this country.")

        except Exception as e:
            st.warning(f"Error reading the selected sheet: {e}")


    # Create the graph
    elif source_country:
        excel_file = os.path.join(fta_data_folder, f"{source_country.lower()}.xlsx")
        if os.path.exists(excel_file):
            try:
                df = pd.read_excel(excel_file, sheet_name=None)
                st.markdown(
                    f"""
                        <div style="text-align: center; margin-top: 10px;">
                        <h1 style="font-size: 40px; font-weight: bold; color: #ffffff; text-shadow: 4px 4px 0 #1a237e, 6px 6px 0 rgba(0, 0, 0, 0.5); font-family: 'Arial Black', sans-serif;">{source_country} EXPORTS TO: </h1>
                
                    """,
                    unsafe_allow_html=True
                )

                # Bar Plot with Error Bars
                sheet_name, sheet_df = list(df.items())[0]
                
                
                # Convert range values to numeric
                def convert_range_to_numeric(value):
                    if isinstance(value, str) and '-' in value:
                        try:
                            values = []
                            for v in value.split('-'):
                                v_strip = v.strip().upper()
                                if v_strip == 'NA':
                                    values.append('NA')
                                else:
                                    values.append(round(float(v_strip), 2))
                            return values
                        except ValueError:
                            return ['NA', 'NA']
                    elif isinstance(value, str) and value.strip().upper() == 'NA':
                        return ['NA', 'NA']
                    else:
                        try:
                            return [round(float(value), 2), round(float(value), 2)]
                        except ValueError:
                            return ['NA', 'NA']
                
                sheet_df[['MFN Tariff_Min', 'MFN Tariff_Max']] = sheet_df['MFN Tariff'].apply(convert_range_to_numeric).tolist()
                sheet_df[['FTA Tariff_Min', 'FTA Tariff_Max']] = sheet_df['FTA Tariff'].apply(convert_range_to_numeric).tolist()
                
                # Create the bar plot data
                bar_plot_data = sheet_df[['Country/Region', 'LC', 'MFN Tariff_Min', 'MFN Tariff_Max', 'FTA Tariff_Min', 'FTA Tariff_Max']]
                bar_plot_data['MFN Tariff'] = (bar_plot_data['MFN Tariff_Min'] + bar_plot_data['MFN Tariff_Max']) / 2
                bar_plot_data['FTA Tariff'] = (bar_plot_data['FTA Tariff_Min'] + bar_plot_data['FTA Tariff_Max']) / 2

                # Create the combined plot
                fig, ax = plt.subplots(figsize=(22, 8), facecolor='None')
                bar_width = 0.3
                x = np.arange(len(bar_plot_data['Country/Region']))

                # MFN tariff rate bar plot
                mfn_bars = ax.bar(x - bar_width/2, bar_plot_data['MFN Tariff'], width=bar_width, color='#4c72b0', alpha=0.6)
                mfn_error = ax.errorbar(x - bar_width/2, bar_plot_data['MFN Tariff'], yerr=[bar_plot_data['MFN Tariff'] - bar_plot_data['MFN Tariff_Min'], bar_plot_data['MFN Tariff_Max'] - bar_plot_data['MFN Tariff']], fmt='none', capsize=14, elinewidth=31, color='#4c72b0')

                # FTA tariff rate bar plot
                fta_bars = ax.bar(x + bar_width/2, bar_plot_data['FTA Tariff'], width=bar_width, color='#55a868', alpha=0.6)
                fta_error = ax.errorbar(x + bar_width/2, bar_plot_data['FTA Tariff'], yerr=[bar_plot_data['FTA Tariff'] - bar_plot_data['FTA Tariff_Min'], bar_plot_data['FTA Tariff_Max'] - bar_plot_data['FTA Tariff']], fmt='none', capsize=14, elinewidth=31, color='#55a868')
                
                # Add the MFN and FTA tariff values and LC text to the bars
                for i, (country_region, lc, mfn_min, mfn_max, fta_min, fta_max) in enumerate(zip(bar_plot_data['Country/Region'], bar_plot_data['LC'], sheet_df['MFN Tariff_Min'], sheet_df['MFN Tariff_Max'], sheet_df['FTA Tariff_Min'], sheet_df['FTA Tariff_Max'])):
                    print(fta_min)
                    if mfn_min == 0 and mfn_max == 0:
                        ax.text(x[i] - bar_width/2, mfn_max + 0.5, "MFN = 0", color='#4c72b0', fontweight='bold', ha='center', va='bottom', fontsize=12, rotation=90)
                    else:
                        ax.text(x[i] - bar_width/2, mfn_max + 0.5, f"{sheet_df['MFN Tariff'][i]}", color='#4c72b0', fontweight='bold', ha='center', va='bottom', fontsize=12)

                        
                    if fta_max!=0:
                        ax.text(x[i] + bar_width/2, fta_min + 0.5, "FTA = Out of Scope", color='green', fontweight='bold', ha='center', va='bottom', fontsize=12, rotation=90)
                    elif fta_min == 0 and fta_max == 0:
                        ax.text(x[i] + bar_width/2, fta_max + 0.5, "FTA = 0", color='green', fontweight='bold', ha='center', va='bottom', fontsize=12, rotation=90)
                    else:
                        ax.text(x[i] + bar_width/2, fta_max + 0.5, f"{sheet_df['FTA Tariff'][i]}", color='green', fontweight='bold', ha='center', va='bottom', fontsize=12)
                    ax.text(x[i], -0.5, f"\n\nLC {lc}", color='orange', fontweight='bold', ha='center', va='top', fontsize=12, rotation=0)
                ax.set_xticks(x)
                ax.set_xticklabels(bar_plot_data['Country/Region'], rotation=0, fontsize=12, fontweight="bold")
                ax.set_xlabel('\n\nCountry/Region', fontsize=18, color="white", fontweight="bold")
                ax.set_ylabel('Tariff Rate', fontsize=18, color="white", fontweight="bold")
                ax.tick_params(axis='both', which='major', labelsize=12)

                # Create the legend
                mfn_label = 'MFN Tariff'
                fta_label = 'FTA Tariff'
                legend_labels = [mfn_label, fta_label,'NA']
                legend_handles = [mfn_bars, fta_bars]


                ax.legend(legend_handles, legend_labels, loc='upper left', fontsize=10)
                # Make the plot background transparent
                fig.patch.set_alpha(0.9)
                ax.patch.set_alpha(0.7)

                # Display the combined plot
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")


            # Check if there are more sheets in the Excel file
            if source_country:
                excel_file = os.path.join(fta_data_folder, f"{source_country.lower()}.xlsx")
                if os.path.exists(excel_file):
                    df = pd.read_excel(excel_file, sheet_name=None)
                    if len(df) > 1:
                        # Get the FTA Negotiations sheet
                        fta_negotiations_sheet_name, fta_negotiations_sheet_df = list(df.items())[1]

                        st.markdown(
                            f"""
                            <div style="text-align: left; margin-top: 10px;">
                                <h1 style="font-size: 40px; font-weight: bold; color: white; text-shadow: 4px 4px 0 #1a237e, 6px 6px 0 rgba(0, 0, 0, 0.5); font-family: 'Arial Black', sans-serif;">FTA under negotiations</h1>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Create the compact expandable sections
                        col_count = 0
                        for _, row in fta_negotiations_sheet_df.iterrows():
                            if col_count % 3 == 0:
                                cols = st.columns(3)
                            with cols[col_count % 3]:
                                expander_title = f"{row['Country/Region']}"
                                st.markdown(
                                    f"""
                                    <div style="background-color: white; color: #4c72b0; padding: 0px; box-shadow: 10px 10px 4px rgba(0, 0, 0, 0.25);border-radius: 50px; text-align: center; font-weight: bold;">
                                        <h2 style="text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); font-size: 20px; font-weight: bold;">{expander_title}</h2>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
    )
                                with st.expander("", expanded=False):
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #ffffff; color: #000000; padding: 20px; border-radius: 20px; box-shadow: 10px 10px 4px rgba(0, 0, 0, 0.25); margin-bottom: 10px; display: flex; justify-content: center;">
                                            <table style="width: 100%; font-size: 14px;">
                                                <tr>
                                                    <th style="text-align: left;">FTA Name</th>
                                                    <td style="word-break: break-word;">{row['FTA Name']}</td>
                                                </tr>
                                                <tr>
                                                    <th style="text-align: left;">Negotiation Status</th>
                                                    <td style="word-break: break-word;">{row['Negotiation Status']}</td>
                                                </tr>
                                                <tr>
                                                    <th style="text-align: left;">Notes</th>
                                                    <td style="word-break: break-word;">{row['Notes']}</td>
                                                </tr>
                                                <tr>
                                                    <th style="text-align: left;">Last Update</th>
                                                    <td style="word-break: break-word;">{row['Last Update']}</td>
                                                </tr>
                                            </table>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            col_count += 1
                    else:
                        st.warning("No FTA negotiation data found in the selected Excel file.")
        
    else:
        st.markdown(f"PLEASE SELECT EXPORT COUNTRY")

elif selected_view == "Country Specific" and selected_import_country:

    try:
        # Initialize an empty list to store dataframes
        country_specific_dfs = []

        # Iterate through all the Excel files
        for excel_file in excel_files:
            file_path = os.path.join(fta_data_folder, f"{excel_file.lower()}.xlsx")
            if os.path.exists(file_path):
                df = pd.read_excel(file_path, sheet_name=None)
                
                # Iterate through all the sheets (except the first 2)
                for sheet_name in list(df.keys())[2:]:
                    sheet_df = df[sheet_name]
                    
                    # Check if the selected import country is present in the sheet
                    if 'Country/Region' in sheet_df.columns:
                        # Locate the first row for the selected import country
                        start_idx = sheet_df[sheet_df['Country/Region'] == selected_import_country].index

                        if not start_idx.empty:
                            # Get the first index of the selected country
                            start_idx = start_idx[0]

                            # Iterate through rows from start_idx onwards
                            for idx in range(start_idx, len(sheet_df)):
                                # Stop if another valid country appears
                                if pd.notnull(sheet_df.loc[idx, 'Country/Region']) and sheet_df.loc[idx, 'Country/Region'] != selected_import_country:
                                    break
                                # Append the rows for the selected import country
                                country_specific_dfs.append(sheet_df.iloc[idx])

        # Convert the list of rows into a DataFrame
        if country_specific_dfs:
            combined_df = pd.DataFrame(country_specific_dfs)
            st.dataframe(combined_df)  # Display the combined DataFrame
        else:
            st.warning(f"No data found for {selected_import_country}.")

    except Exception as e:
        st.error(f"Error processing data for {selected_import_country}: {e}")



else:
    st.markdown(f"PLEASE SELECT SPECIFIC COUNTRY")