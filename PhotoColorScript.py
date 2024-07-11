from PIL import Image
import numpy as np
import os

def get_most_common_color(image_path):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        data = np.array(img)
        data = data.reshape((-1, 3))
        colors, count = np.unique(data, axis=0, return_counts=True)
        return colors[count.argmax()]

def process_folder(folder_path):
    colors = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            colors.append(get_most_common_color(image_path))
    if colors:
        average_color = np.mean(colors, axis=0).astype(int)
        return tuple(average_color)
    else:
        return None

# Create a wallpaper for iPhone 14 Pro
def create_wallpaper(average_color, width=1170, height=2532, file_path='iphone_14_pro_wallpaper.jpg'):
    # Create a new image with the average color
    wallpaper = Image.new('RGB', (width, height), color=average_color)
    # Save the wallpaper
    wallpaper.save(file_path)
    print(f"Wallpaper saved to {file_path}")
    


folder_path = 'photos'
average_color = process_folder(folder_path)
if average_color:
    print(f"The average of the most common colors in the images is: {average_color}")
    create_wallpaper(average_color)
else:
    print("No JPG images found in the folder.")
