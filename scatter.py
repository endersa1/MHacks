import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
csv_path = 'eye_gaze_coordinates.csv'
df = pd.read_csv(csv_path)

# Extract relevant columns
scatter_data = df[['Normalized X', 'Normalized Y']]

# Create a scatter plot using Matplotlib
fig, ax = plt.subplots()
ax.scatter(scatter_data['Normalized X'], scatter_data['Normalized Y'])
ax.set_xlabel('Normalized X')
ax.set_ylabel('Normalized Y')
ax.set_title('Eye Gaze Scatter Plot')

# Display the scatter plot using Streamlit
st.pyplot(fig)
