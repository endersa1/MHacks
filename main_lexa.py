from fastapi import FastAPI
import cv2
import time
#import dlib
#import pyautogui
import csv
from pymongo import MongoClient
import streamlit as st
import requests

app = FastAPI()

# Replace <your_connection_string> with your MongoDB Atlas connection string
client = MongoClient("mongodb+srv://endersa:Carmex334@cluster0.ealr11t.mongodb.net/")
db = client["user_data"]

@app.get("/")
def read_root():
    return {"Hello": "World"}


# Example MongoDB query
@app.get("/users")
def get_users():
    users = db.users.find()
    return {"users": list(users)}


@app.get("/analyze")
def analyze_image():
    # Your computer vision logic here
    # e.g., read an image, process, and return results

    return {"result": "Image analyzed"}

# app.py

st.title("Your App Title")

# Your Streamlit app code goes here

# Example API request
response = requests.get("http://localhost:8000/")
st.write(response.json())