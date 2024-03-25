from openai import OpenAI
import urllib.request
import csv
import os
from PIL import Image, ImageDraw, ImageFont
import hashlib

client = OpenAI()

# load quotes
with open("quotes.csv", "r") as file:
    reader = csv.reader(file, delimiter=";")
    quotes = list(reader)

# create prompts for each quote
prompts = [
    f"An image visualizing the essence of the following quote without any text in it and in the a style of the authors time: {quote}"
    for quote in quotes
]
fnames = [hashlib.md5(prompt.encode()).hexdigest() for prompt in prompts]
fnames = [f"{fname}.jpg" for fn0ame in fnames]

# create visualizations
visualizations = os.listdir("visualizations")
for prompt, fname in zip(prompts, fnames):
    if fname not in visualizations:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        f_out = os.path.join("visualizations", fname)
        urllib.request.urlretrieve(image_url, f_out)
        print(f"Downloaded {f_out}")
    else:
        print(f"Skipping {fname}")

# create wallpapers
resolution = [3840, 2160]
wallpapers = os.listdir("wallpapers")

for prompt, fname in zip(prompts, fnames):
    if fname not in wallpapers:
        # create black background
        img = Image.new("RGB", resolution, (0, 0, 0))
        # load visualization
        visualization = Image.open(os.path.join("visualizations", fname))
        # center visualization in background
        x = (resolution[0] - visualization.width) // 2
        y = (resolution[1] - visualization.height) // 2
        img.paste(visualization, (x, y))
        # add quote below visualization in white and textsize 20
        quote = quotes[fnames.index(fname)][0]
        img_draw = ImageDraw.Draw(img)
        text_size = 60  # Adjust the text size as desired

        font = ImageFont.truetype("georgia.ttf", text_size)  # Specify the font and size
        # Calculate the x-coordinate to center the text
        text_width = img_draw.textlength(quote, font=font)
        # add a newline to the quote if it is too long
        multiline = False
        if text_width > resolution[0]:
            multiline = True
            quote = (
                quote[: len(quote) // 2] + "\n" + quote[len(quote) // 2 :].strip(" ")
            )
            text_width = text_width // 2
        x = (resolution[0] - text_width) // 2
        y = y + visualization.height + 100
        img_draw.text((x, y), quote, (255, 255, 255), font=font)
        # add author below quote in white and textsize 40
        author = quotes[fnames.index(fname)][1]
        font = ImageFont.truetype("georgia.ttf", 40)
        text_width = img_draw.textlength(author, font=font)
        x = (resolution[0] - text_width) // 2
        if multiline:
            y = y + 2 * text_size + 20
        else:
            y = y + text_size + 20
        img_draw.text(
            (x, y),
            author,
            (255, 255, 255),
            font=font,
        )

        # save wallpaper
        f_out = os.path.join("wallpapers", fname)
        img.save(f_out)
        print(f"Saved wallpaper {f_out}")
    else:
        print(f"Skipping wallpaper {fname}")
