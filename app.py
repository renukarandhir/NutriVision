import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import re

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def extract_nutritional_data(response_text):
    nutritional_info = {}
    lines = response_text.split("\n")
    for line in lines:
        if "calories" in line:  # Looking for lines with calorie information
            parts = line.split("-")
            if len(parts) == 2:  # Ensure we have two parts to split
                item = parts[0].strip()
                calories_match = re.search(r'(\d+)', parts[1])  # Match numerical calorie value
                if calories_match:
                    calories = calories_match.group(1)
                    try:
                        calories = int(calories)
                    except ValueError:
                        calories = 0
                    nutritional_info[item] = calories
    return nutritional_info

def plot_nutritional_chart(nutritional_info, title):
    plt.clf()  # Clear the current figure
    labels = nutritional_info.keys()
    sizes = nutritional_info.values()

    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Style the pie chart
    for text in texts:
        text.set_size(10)  # Set size for the labels
    for autotext in autotexts:
        autotext.set_color('white')  # Set color for the percentages
        autotext.set_size(10)  # Set size for the percentage text

    plt.title(title)  # Set the title for the chart
    st.pyplot(plt)  # Display the plot in the Streamlit app

## Initialize our Streamlit app
st.set_page_config(page_title="NutriVision App 🥗")

st.header("NutriVision App 🥗")
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Give detailed analysis")

input_prompt = """
You are an expert in nutritionist where you need to see the food items from the image then firstly give a short detailed
    description of the food items or dish in the image 
               and calculate the total calories, also provide the details of every food items with calories intake
               is below format

               1. Item 1 - no of calories
               2. Item 2 - no of calories
               ----
               ----
            Then you can also provide whether the food is healthy or not and also mention the percentage split of
            the ratio of carbohydrates, proteins, fats, fibers, sugar and other import things required in our diet
            
            Now provide a detailed carbon footprint of the food items in the image in the below format and also tell if eating 
            that food is good for the environment or not
            1. Item 1 - carbon footprint
            2. Item 2 - carbon footprint
            ----
            ----
"""

## If submit button is clicked
if submit:
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_prompt, image_data)
    
    # Display the detailed analysis separately from the chart
    st.subheader("Detailed analysis on the dish - ")
    st.write(response)
    
    # Extract nutritional information from the response
    nutritional_info = extract_nutritional_data(response)

    # Check if nutritional_info is empty
    if nutritional_info:
        # Plot the nutritional chart with extracted data
        plot_nutritional_chart(nutritional_info, title="Nutritional Breakdown of Food Items")
    else:
        st.write("No nutritional information found in the response.")

    st.download_button(
        label="Download Analysis Report",
        data=response,
        file_name='analysis_report.txt',
        mime='text/plain'
    )
