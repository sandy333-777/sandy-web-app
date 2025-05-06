import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Insecticide Usage for Pests")

uploaded_file = st.file_uploader("Upload Insecticide Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        required_cols = {'PEST', 'INSECTICIDE', 'Formulation', 'CROP'}
        if required_cols.issubset(df.columns):

            show_all = st.checkbox("Show All Data")

            pest_input = ""
            if not show_all:
                pest_input = st.text_input("Enter Pest Name (partial, case-insensitive):")

            if show_all:
                filtered_df = df.copy()
            elif pest_input:
                filtered_df = df[df['PEST'].str.contains(pest_input, case=False, na=False)]
            else:
                filtered_df = pd.DataFrame()

            if not filtered_df.empty:
                # Crop filter
                crop_options = filtered_df['CROP'].dropna().unique().tolist()
                selected_crop = st.selectbox("Filter by Crop", ["All"] + crop_options)

                if selected_crop != "All":
                    filtered_df = filtered_df[filtered_df['CROP'] == selected_crop]

                # Insecticide filter
                insecticide_options = filtered_df['INSECTICIDE'].dropna().unique().tolist()
                selected_insecticide = st.selectbox("Filter by Insecticide", ["All"] + insecticide_options)

                if selected_insecticide != "All":
                    filtered_df = filtered_df[filtered_df['INSECTICIDE'] == selected_insecticide]

                # Final display
                if not filtered_df.empty:
                    st.write("### Filtered Results")
                    st.dataframe(filtered_df[['PEST', 'INSECTICIDE', 'Formulation', 'CROP']])

                    final_options = filtered_df['INSECTICIDE'].dropna().unique().tolist()
                    insecticide_selection = st.selectbox("Select Insecticide for Details", final_options)

                    if insecticide_selection:
                        selected_data = filtered_df[filtered_df['INSECTICIDE'] == insecticide_selection]
                        formulation = selected_data['Formulation'].iloc[0] if not selected_data.empty else "N/A"
                        pest_names = ", ".join(selected_data['PEST'].dropna().unique())

                        st.markdown(
                            f"### Insecticide Information\n"
                            f"- **Insecticide**: `{insecticide_selection}`\n"
                            f"- **Pests**: `{pest_names}`\n"
                            f"- **Formulation**: `{formulation}`"
                        )

                    # Bar Chart
                    chart_data = filtered_df.dropna(subset=['INSECTICIDE', 'Formulation'])
                    chart_data['Label'] = chart_data['INSECTICIDE'] + " (" + chart_data['Formulation'] + ")"
                    chart_counts = chart_data['Label'].value_counts().reset_index()
                    chart_counts.columns = ['Label', 'Count']

                    fig, ax = plt.subplots(figsize=(10, max(4, len(chart_counts) * 0.4)))
                    chart_counts.sort_values("Count").plot.barh(x='Label', y='Count', ax=ax, color='lightgreen', edgecolor='black')
                    ax.set_title("Insecticide Frequency")
                    st.pyplot(fig)

                else:
                    st.warning("No data after filtering.")
            else:
                st.info("Please enter a valid pest name to begin filtering.")
        else:
            st.error("Excel must contain columns: PEST, INSECTICIDE, Formulation, and CROP.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload an Excel file.")
