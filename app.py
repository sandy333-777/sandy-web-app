import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Insecticide Usage for Pests")

# Create a single column layout
col1 = st.columns([1])[0]

with col1:
    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Insecticide Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            # Read the uploaded Excel file
            df = pd.read_excel(uploaded_file)

            # Strip spaces from column names
            df.columns = df.columns.str.strip()

            # Check required columns
            if {'PEST', 'INSECTICIDE', 'Formulation', 'CROP'}.issubset(df.columns):
                # Pest input
                pest_input = st.text_input("Enter Pest Name (partial or full):")

                if pest_input:
                    # Filter by pest name
                    filtered_df = df[df['PEST'].str.contains(pest_input, case=False, na=False)]

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
                            st.write(f"### Filtered Results for: `{pest_input}`")
                            filtered_df_display = filtered_df[['INSECTICIDE', 'Formulation', 'CROP']]
                            st.dataframe(filtered_df_display)

                            # Insecticide selection for info box
                            final_insecticide_options = filtered_df['INSECTICIDE'].dropna().unique()
                            insecticide_selection = st.selectbox("Select Insecticide for Details", final_insecticide_options)

                            if insecticide_selection:
                                selected_data = filtered_df[filtered_df['INSECTICIDE'] == insecticide_selection]
                                formulation = selected_data['Formulation'].iloc[0]

                                message = (
                                    f"### Insecticide Information\n\n"
                                    f"- **Insecticide**: `{insecticide_selection}`\n"
                                    f"- **Pest**: `{pest_input}`\n"
                                    f"- **Formulation**: `{formulation}`"
                                )
                                st.markdown(message)

                            # Frequency plot
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

                            ax.set_title(f"Insecticides for Pests Matching: {pest_input}", fontsize=14)
                            ax.set_xlabel("Count")
                            ax.set_ylabel("Insecticide (Formulation)")
                            st.pyplot(fig)

                        else:
                            st.warning("No data after applying crop/insecticide filters.")
                    else:
                        st.warning("No matching pests found.")
                else:
                    st.info("Please enter a pest name to search.")
            else:
                st.error("Excel file must contain 'PEST', 'INSECTICIDE', 'Formulation', and 'CROP' columns.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
    else:
        st.info("Please upload an Excel file to begin.")
