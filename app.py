import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Insecticide Usage for Pests")

# Single column layout
col1 = st.columns([1])[0]

with col1:
    # File upload
    uploaded_file = st.file_uploader("Upload Insecticide Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()  # Clean column names

            # Check required columns
            if {'PEST', 'INSECTICIDE', 'Formulation', 'CROP'}.issubset(df.columns):
                # Show All toggle
                show_all = st.checkbox("Show All Data")

                # Pest input (only if not showing all)
                pest_input = ""
                if not show_all:
                    pest_input = st.text_input("Enter Pest Name (partial or full):")

                # Filter pest
                if show_all:
                    filtered_df = df.copy()
                elif pest_input:
                    filtered_df = df[df['PEST'].str.contains(pest_input, case=False, na=False)]
                else:
                    filtered_df = pd.DataFrame()

                if not filtered_df.empty:
                    # Crop filter
                    crop_options = filtered_df['CROP'].dropna().unique().tolist()
                    selected_crop = st.selectbox("Filter by Crop (Optional)", ["All"] + crop_options)

                    if selected_crop != "All":
                        filtered_df = filtered_df[filtered_df['CROP'] == selected_crop]

                    # Insecticide filter
                    insecticide_options = filtered_df['INSECTICIDE'].dropna().unique().tolist()
                    selected_insecticide = st.selectbox("Filter by Insecticide (Optional)", ["All"] + insecticide_options)

                    if selected_insecticide != "All":
                        filtered_df = filtered_df[filtered_df['INSECTICIDE'] == selected_insecticide]

                    if not filtered_df.empty:
                        st.write("### Filtered Results")
                        st.dataframe(filtered_df[['PEST', 'INSECTICIDE', 'Formulation', 'CROP']])


                        # Insecticide selection for detailed info
                        final_insecticide_options = filtered_df['INSECTICIDE'].dropna().unique()
                        insecticide_selection = st.selectbox("Select Insecticide for Details", final_insecticide_options)

                        if insecticide_selection:
                            selected_data = filtered_df[filtered_df['INSECTICIDE'] == insecticide_selection]
                            formulation = selected_data['Formulation'].iloc[0]
                            display_pest = selected_data['PEST'].iloc[0] if not show_all else "Various"

                            st.markdown(
                                f"### Insecticide Information\n\n"
                                f"- **Insecticide**: {insecticide_selection}\n"
                                f"- **Pest**: {display_pest}\n"
                                f"- **Formulation**: {formulation}"
                            )

                        # Bar chart
                        plot_df = filtered_df.dropna(subset=['INSECTICIDE', 'Formulation'])
                        plot_df['INSECTICIDE'] = plot_df['INSECTICIDE'].astype(str)
                        plot_df['Formulation'] = plot_df['Formulation'].astype(str)

                        insecticide_counts = plot_df[['INSECTICIDE', 'Formulation']].value_counts().reset_index(name='Count')
                        insecticide_counts['Label'] = insecticide_counts['INSECTICIDE'] + " (" + insecticide_counts['Formulation'] + ")"

                        fig_height = max(6, 0.5 * len(insecticide_counts))
                        fig, ax = plt.subplots(figsize=(12, fig_height))
                        insecticide_counts.sort_values("Count").plot(
                            kind='barh', x='Label', y='Count', ax=ax, color='skyblue', edgecolor='black'
                        )

                        title = "Insecticide Frequency"
                        if not show_all and pest_input:
                            title += f" for Pests Matching: {pest_input}"
                        ax.set_title(title, fontsize=14)
                        ax.set_xlabel("Count")
                        ax.set_ylabel("Insecticide (Formulation)")
                        st.pyplot(fig)

                    else:
                        st.warning("No data after applying filters.")
                else:
                    if not show_all:
                        st.info("Please enter a pest name to search.")
                    else:
                        st.warning("No data available.")
            else:
                st.error("Excel file must contain 'PEST', 'INSECTICIDE', 'Formulation', and 'CROP' columns.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
    else:
        st.info("Please upload an Excel file to begin.") 
