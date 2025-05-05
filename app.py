import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page title
st.set_page_config(page_title="Insecticide Usage", layout="wide")
st.title("🧪 Insecticide Usage for Pests")

# Upload Excel file
uploaded_file = st.file_uploader("📄 Upload Insecticide Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        required_columns = {'PEST', 'INSECTICIDE', 'Formulation', 'CROP'}
        if required_columns.issubset(set(df.columns)):

            # Optional CSS to center content
            st.markdown("""
                <style>
                .block-container {
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                }
                </style>
            """, unsafe_allow_html=True)

            # Pest input and show-all checkbox in a row
            col1, col2 = st.columns([3, 1])
            with col1:
                pest_input = st.text_input("🔍 Enter Pest Name (partial or full):")
            with col2:
                show_all = st.checkbox("Show All Data")

            if show_all or pest_input:
                if show_all:
                    filtered_df = df.copy()
                else:
                    filtered_df = df[df['PEST'].str.contains(pest_input, case=False, na=False)]

                if not filtered_df.empty:
                    # Dropdown filters for Crop and Insecticide
                    crop_options = sorted(filtered_df['CROP'].dropna().unique().tolist())
                    insecticide_options = sorted(filtered_df['INSECTICIDE'].dropna().unique().tolist())

                    col3, col4 = st.columns(2)
                    with col3:
                        selected_crop = st.selectbox("🌱 Filter by Crop", ["All"] + crop_options)
                    with col4:
                        selected_insecticide = st.selectbox("🧴 Filter by Insecticide", ["All"] + insecticide_options)

                    # Apply crop and insecticide filter
                    if selected_crop != "All":
                        filtered_df = filtered_df[filtered_df['CROP'] == selected_crop]
                    if selected_insecticide != "All":
                        filtered_df = filtered_df[filtered_df['INSECTICIDE'] == selected_insecticide]

                    if not filtered_df.empty:
                        st.write(f"### 🐛 Filtered Results ({len(filtered_df)} records)")
                        st.dataframe(filtered_df[['CROP', 'PEST', 'INSECTICIDE', 'Formulation']])

                        # Insecticide selection section
                        final_insecticide_options = filtered_df['INSECTICIDE'].unique().tolist()

                        with st.container():
                            insecticide_selection = st.selectbox("🔽 Select Insecticide for Details", final_insecticide_options)
                            if insecticide_selection:
                                selected_data = filtered_df[filtered_df['INSECTICIDE'] == insecticide_selection]
                                formulation = selected_data['Formulation'].iloc[0]
                                st.markdown(f"""
                                ### 🧾 Insecticide Information
                                - **Insecticide**: `{insecticide_selection}`
                                - **Pest**: `{pest_input if not show_all else 'All'}`
                                - **Formulation**: `{formulation}`
                                """)

                        # Bar Chart
                        insecticide_counts = filtered_df[['INSECTICIDE', 'Formulation']].value_counts().reset_index(name='Count')
                        insecticide_counts['Label'] = insecticide_counts['INSECTICIDE'] + " (" + insecticide_counts['Formulation'] + ")"

                        fig_height = max(6, 0.5 * len(insecticide_counts))
                        fig, ax = plt.subplots(figsize=(12, fig_height))
                        insecticide_counts.sort_values("Count").plot(
                            kind='barh', x='Label', y='Count',
                            ax=ax, color='skyblue', edgecolor='black'
                        )
                        ax.set_title(f"Insecticides Used (Pest: {pest_input if not show_all else 'All'})", fontsize=14)
                        ax.set_xlabel("Usage Count")
                        ax.set_ylabel("Insecticide (Formulation)")
                        st.pyplot(fig)
                    else:
                        st.warning("No matching records found after filter.")
                else:
                    st.warning("No matching pests found.")
            else:
                st.info("Please enter a pest name or enable 'Show All Data'.")

        else:
            st.error("Excel file must contain these columns: 'PEST', 'INSECTICIDE', 'Formulation', 'CROP'.")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Upload an Excel file to begin.")
