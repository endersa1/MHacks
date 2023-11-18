import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np

def display_heatmap(csv_path, title):
    # Load CSV data
    df = pd.read_csv(csv_path)

    # Extract relevant columns
    scatter_data = df[['Normalized X', 'Normalized Y']]

    # Calculate kernel density estimate for the data
    kde = gaussian_kde(scatter_data.T)

    # Create a grid of coordinates for the heatmap
    x_grid, y_grid = np.mgrid[scatter_data['Normalized X'].min():scatter_data['Normalized X'].max():100j,
                              scatter_data['Normalized Y'].max():scatter_data['Normalized Y'].min():100j]
    positions = np.vstack([x_grid.ravel(), y_grid.ravel()])
    z = np.reshape(kde(positions).T, x_grid.shape)

    # Create a heatmap without scatter plot
    fig, ax = plt.subplots()
    ax.imshow(np.rot90(z), cmap=plt.cm.viridis, extent=[scatter_data['Normalized X'].min(),
                                                       scatter_data['Normalized X'].max(),
                                                       scatter_data['Normalized Y'].min(),
                                                       scatter_data['Normalized Y'].max()],
              alpha=0.5, aspect='auto')
    ax.set_xlabel('Normalized X')
    ax.set_ylabel('Normalized Y')
    ax.set_title(title)

    # Display the heatmap using Streamlit
    st.pyplot(fig)

# Display heatmap for top_right.csv
display_heatmap('top_right.csv', 'Top Right Heatmap')

# Display heatmap for bottom_left.csv
display_heatmap('bottom_left.csv', 'Bottom Left Heatmap')