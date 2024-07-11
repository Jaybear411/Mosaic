from PIL import Image, ImageStat
import requests
from io import BytesIO
from openai import OpenAI

client = OpenAI(
    api_key='goes here lol'
)

def get_dominant_color(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((1, 1))
    dominant_color = img.getpixel((0, 0))
    return '#%02x%02x%02x' % dominant_color


def overlay_image(background_path, overlay_image, position=(0, 0)):
    background = Image.open(background_path)

    overlay_image_resized = overlay_image.resize((background.width // 2, background.height // 2), Image.Resampling.LANCZOS)
    
    background.paste(overlay_image_resized, position, overlay_image_resized.convert('RGBA'))
    return background


def generate_image_from_prompt(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    image_url = response.data[0].url

    response = requests.get(image_url)

    image = Image.open(BytesIO(response.content))
    return image


if __name__ == "__main__":
    wallpaper_path = "iphone_14_pro_wallpaper.jpg" 
    dominant_color = get_dominant_color(wallpaper_path)
    prompt = f"Mountains with river crossing through it composed with shades of {dominant_color}"  # Your desired prompt with color
    overlay_img = generate_image_from_prompt(prompt)
    position = (100, 100)
    result_image = overlay_image(wallpaper_path, overlay_img, position=position)
    result_image.save("result_wallpaper4.jpg")