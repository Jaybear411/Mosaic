#My_key: 
#New_key: 

import os
import base64
import shutil
import requests
from collections import Counter
from typing import List
from openai import OpenAI
from PIL import Image, ImageOps
import piexif
from iptcinfo3 import IPTCInfo

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=''
)

# Initialize the OpenAI client with your API key
api_key = '' 

def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

existing_keywords = []

def image_to_text(image_base64: str, existing_keywords: List[str]) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Use the API key directly
    }
    payload = {
        "model": "gpt-4-vision-preview",  # Hypothetical model name
        "prompt": f"I want 5 general keywords that describe the image. If it is a tiger, the keywords should include 'tiger' and 'animal'. These keywords are already present: {existing_keywords} Please output them comma separated. Please as the first entry, output an editorialized title, also separated by commas. Don't output any other characters.",  # Adjust according to actual API documentation
        "max_tokens": 300,
        "data": f"data:image/jpeg;base64,{image_base64}"  # Example, adjust according to actual API documentation
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_json = response.json()
        try:
            content = response_json["choices"][0]["message"]["content"]
            return content
        except KeyError:
            print(f"Error processing response: {response_json}")
            return ""
    else:
        print(f"HTTP Error: {response.status_code}")
        try:
            print(response.json())  # Attempt to print JSON response
        except ValueError:
            print(response.text)   # If response is not JSON, print raw response
        return ""

def analyze_descriptions(descriptions: List[str]) -> List[str]:
    words = []
    for description in descriptions:
        words.extend(description.lower().replace('.', '').replace(',', '').split())
    word_counts = Counter(words)
    common_stopwords = {'the', 'and', 'a', 'to', 'of', 'in', 'on', 'with', 'as', 'for', 'is', 'at', 'it', 'this', 'that', 'these', 'those'}
    common_words = [word for word, count in word_counts.items() if count > 1 and word not in common_stopwords]
    return common_words

def resize_image(image_path: str, output_path: str, target_size=(400, 400)) -> None:
    with Image.open(image_path) as img:
        img_resized = ImageOps.exif_transpose(img)  # Corrects the orientation if necessary
        img_resized = img_resized.resize(target_size)

        # Convert RGBA to RGB if necessary
        if img_resized.mode == 'RGBA':
            img_resized = img_resized.convert('RGB')

        img_resized.save(output_path, format='JPEG', quality=90)

def update_image_metadata(image_path: str, new_title: str, keywords: List[str]) -> None:
    info = IPTCInfo(image_path)
    if new_title:
        info['object name'] = new_title
    if keywords:
        info['keywords'] = keywords
    info.save()

def main(folder_path: str):
    if not os.path.exists(folder_path):
        print("Folder path does not exist")
        return

    descriptions = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            original_image_path = os.path.join(folder_path, file_name)
            resized_image_path = os.path.join(folder_path, f"resized_{file_name}")
            resize_image(original_image_path, resized_image_path)
            image_base64 = encode_image_base64(resized_image_path)
            description = image_to_text(image_base64, existing_keywords)
            if description:
                print(description)
                descriptions.append(description)
                print(f"Description for {file_name}: {description}")
            # Update the image metadata (optional)
            # update_image_metadata(resized_image_path, "Your New Title", ["keyword1", "keyword2"])
            os.remove(resized_image_path)

    if descriptions:
        common_themes = analyze_descriptions(descriptions)
        print("Common themes found:", common_themes)
    else:
        print(descriptions)
        print("No descriptions found to analyze.")

if __name__ == "__main__":
    main("AnimalPhotos")
