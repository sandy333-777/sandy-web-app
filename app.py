import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Insecticide Usage for Pests")

# Create a single column for layout (left side only)
col1 = st.columns([1])[0]  # Only one column to take the whole page

with col1:
    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Insecticide Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            # Read the uploaded Excel file
            df = pd.read_excel(uploaded_file)

            # Strip any leading/trailing spaces in the column names
            df.columns = df.columns.str.strip()

            # Check if required columns exist
            if 'PEST' in df.columns and 'INSECTICIDE' in df.columns and 'Formulation' in df.columns:
                # Step 1: Text input for pest name
                pest_input = st.text_input("Enter Pest Name (partial or full):")

                if pest_input:
                    # Step 2: Filter pest case-insensitively
                    filtered_df = df[df['PEST'].str.contains(pest_input, case=False, na=False)]

                    if not filtered_df.empty:
                        # Show filtered results
                        st.write(f"### Filtered Results for pests matching: `{pest_input}`")
                        filtered_df = filtered_df[['INSECTICIDE', 'Formulation','CROP']]
                        st.dataframe(filtered_df)

                        # Step 3: Dropdown to select insecticide from filtered results
                        insecticide_options = filtered_df['INSECTICIDE'].unique()
                        insecticide_selection = st.selectbox("Select Insecticide", insecticide_options)

                        # Based on the selection, generate a formatted message
                        if insecticide_selection:
                            selected_data = filtered_df[filtered_df['INSECTICIDE'] == insecticide_selection]
                            formulation = selected_data['Formulation'].iloc[0]  # Get the first formulation

                            # Step 4: Formatted message display
                            message = (
                                f"### Insecticide Information\n\n"
                                f"- **Insecticide**: `{insecticide_selection}`\n"
                                f"- **Pest**: `{pest_input}`\n"
                                f"- **Formulation**: `{formulation}`"
                            )
                            st.markdown(message)
                            

                        # Insecticide frequency count for the plot
                        # Insecticide frequency count

                        # Drop rows with missing values in key columns
                        filtered_df = filtered_df.dropna(subset=['INSECTICIDE', 'Formulation'])

                        # Convert both columns to strings to avoid type errors
                        filtered_df['INSECTICIDE'] = filtered_df['INSECTICIDE'].astype(str)
                        filtered_df['Formulation'] = filtered_df['Formulation'].astype(str)

                        # Group and count
                        insecticide_counts = (
                            filtered_df.groupby(['INSECTICIDE', 'Formulation'])
                            .size()
                            .reset_index(name='Count')
                        )


                        
                        insecticide_counts = filtered_df[['INSECTICIDE', 'Formulation']].value_counts().reset_index(name='Count')

                        # Combine INSECTICIDE and FORMULATION for unique display
                        insecticide_counts['Label'] = insecticide_counts['INSECTICIDE'].astype(str) + " (" + insecticide_counts['Formulation'].astype(str) + ")"

                        # Calculate figure height dynamically (e.g., 0.5 inch per label)
                        fig_height = max(6, 0.5 * len(insecticide_counts))

                        # Plot
                        fig, ax = plt.subplots(figsize=(12, fig_height))
                        insecticide_counts.sort_values("Count") \
                                  .plot(kind='barh', x='Label', y='Count', ax=ax, color='skyblue', edgecolor='black')

                        ax.set_title(f"Insecticides for Pests Matching: {pest_input}", fontsize=14)
                        ax.set_xlabel("Count")
                        ax.set_ylabel("Insecticide (Formulation)")
                        st.pyplot(fig)

                    else:
                        st.warning("No matching pests found.")
                else:
                    st.info("Please enter a pest name to search.")
            else:
                st.error("Excel file must contain 'PEST', 'INSECTICIDE', and 'Formulation' columns.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
    else:
        st.info("Please upload an Excel file to begin.")
