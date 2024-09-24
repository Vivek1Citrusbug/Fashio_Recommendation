import os
import streamlit as st
import requests
import json
import uuid
from PIL import Image
from io import BytesIO

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")  

url_file_path = 'public_Image_Url/publicUrl.json'

def upload_to_imgur(image_file,unique_filename):
    url = "https://api.imgur.com/3/image"
    print(image_file)
    files = [
        ('image', (image_file.name, image_file.read(), 'image/jpeg'))
    ]
    headers = {
        'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'
    }
    payload = {
        'title': unique_filename, 
        'type': 'image'
    }
    response = requests.post(url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        data = response.json()
        imgur_link = data["data"]["link"]
        
        image_metadata = {
            'id': unique_filename,
            'deletehash': data['data']['deletehash'],
            'title': data['data']['title'],
            'description': data['data']['description'],
            'type': data['data']['type'],
            'width': data['data']['width'],
            'height': data['data']['height'],
            'size': data['data']['size'],
            'link': imgur_link,
        }
        return imgur_link, image_metadata
    else:
        st.error(f"Failed to upload image. Status Code: {response.status_code}")
        return None, None

def store_image_metadata(image_metadata):
    try:
        if os.path.exists(url_file_path):
            with open(url_file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("JSON file is Starting with an empty dictionary.")
                    data = {}
        else:
            data = {}

        data[image_metadata['id']] = {
            'link': image_metadata['link'],
        }

        with open(url_file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print("Error: The specified file path does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

st.title("Fashion Item Image Upload to Imgur")
uploaded_files = st.file_uploader("Choose an image of your fashion item...", type=["png", "jpg", "jpeg"],accept_multiple_files=True)
print(type(uploaded_files))
if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        st.write("File Name:", uploaded_file.name)

    if st.button("Upload to Imgur"):
        for uploaded_file in uploaded_files:
            #generating UUID for our filename. 
            unique_filename = str(uuid.uuid4()) 
            image_url, image_metadata = upload_to_imgur(uploaded_file,unique_filename)
            
            if image_url:
                store_image_metadata(image_metadata)
                st.subheader("Image Metadata")
                st.write(f"**ID:** {image_metadata['id']}")
                st.write(f"**Title:** {image_metadata['title']}")
                st.write("**Public URL:**", image_url)
                st.image(image_url, caption=image_metadata['id'], width=300)
