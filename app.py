import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Insecticide Usage for Pests")

# Upload Excel
uploaded_file = st.file_uploader("Upload Insecticide Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()  # Clean column names

        required_columns = {'PEST', 'INSECTICIDE', 'Formulation', 'CROP'}
        if required_columns.issubset(df.columns):
            # Show all data toggle
            show_all = st.checkbox("Show All Data")

            # Text inputs for filtering (partial, case-insensitive)
            pest_input = ""
            crop_input = ""
            insecticide_input = ""

            if not show_all:
                pest_input = st.text_input("Enter Pest Name (partial):")
                crop_input = st.text_input("Enter Crop Name (partial):")
                insecticide_input = st.text_input("Enter Insecticide Name (partial):")

            # Apply filters
            filtered_df = df.copy()

            if not show_all:
                if pest_input:
                    filtered_df = filtered_df[filtered_df['PEST'].str.contains(pest_input, case=False, na=False)]
                if crop_input:
                    filtered_df = filtered_df[filtered_df['CROP'].str.contains(crop_input, case=False, na=False)]
                if insecticide_input:
                    filtered_df = filtered_df[filtered_df['INSECTICIDE'].str.contains(insecticide_input, case=False, na=False)]

            if not filtered_df.empty:
                # Display table with PEST column
                st.write("### Filtered Results")
                st.dataframe(filtered_df[['PEST', 'INSECTICIDE', 'Formulation', 'CROP']])

                # Dropdown for detailed info only if insecticides exist
                insecticide_list = filtered_df['INSECTICIDE'].dropna().unique().tolist()
                if insecticide_list:
                    selected_insecticide = st.selectbox("Select Insecticide for Details", insecticide_list)

                    selected_data = filtered_df[filtered_df['INSECTICIDE'] == selected_insecticide]
                    if not selected_data.empty:
                        formulation = selected_data['Formulation'].iloc[0]
                        display_pest = selected_data['PEST'].iloc[0] if not show_all else "Various"

                        st.markdown(
                            f"### Insecticide Information\n\n"
                            f"- **Insecticide**: `{selected_insecticide}`\n"
                            f"- **Pest**: `{display_pest}`\n"
                            f"- **Formulation**: `{formulation}`"
                        )

                # Bar chart
                chart_df = filtered_df.dropna(subset=['INSECTICIDE', 'Formulation'])
                if not chart_df.empty:
                    chart_df['INSECTICIDE'] = chart_df['INSECTICIDE'].astype(str)
                    chart_df['Formulation'] = chart_df['Formulation'].astype(str)
                    count_df = chart_df[['INSECTICIDE', 'Formulation']].value_counts().reset_index(name='Count')
                    count_df['Label'] = count_df['INSECTICIDE'] + " (" + count_df['Formulation'] + ")"

                    fig_height = max(6, 0.5 * len(count_df))
                    fig, ax = plt.subplots(figsize=(12, fig_height))
                    count_df.sort_values("Count").plot(
                        kind='barh', x='Label', y='Count', ax=ax, color='skyblue', edgecolor='black'
                    )
                    ax.set_title("Insecticide Frequency", fontsize=14)
                    ax.set_xlabel("Count")
                    ax.set_ylabel("Insecticide (Formulation)")
                    st.pyplot(fig)
                else:
                    st.warning("Not enough data to display a chart.")
            else:
                st.warning("No data after applying filters.")
        else:
            st.error(f"Excel must contain columns: {', '.join(required_columns)}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload an Excel file.")
