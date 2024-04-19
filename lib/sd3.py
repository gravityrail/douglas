import requests
from enum import Enum

class ImageStylePresets(Enum):
	THREE_D_MODEL = "3d-model"
	ANALOG_FILM = "analog-film"
	ANIME = "anime"
	CINEMATIC = "cinematic"
	COMIC_BOOK = "comic-book"
	DIGITAL_ART = "digital-art"
	ENHANCE = "enhance"
	FANTASY_ART = "fantasy-art"
	ISOMETRIC = "isometric"
	LINE_ART = "line-art"
	LOW_POLY = "low-poly"
	MODELING_COMPOUND = "modeling-compound"
	NEON_PUNK = "neon-punk"
	ORIGAMI = "origami"
	PHOTOGRAPHIC = "photographic"
	PIXEL_ART = "pixel-art"
	TILE_TEXTURE = "tile-texture"


class ImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key

    def run(self, prompt, path, style_preset=ImageStylePresets.COMIC_BOOK.value):
        print(
            f"Generating image for prompt: {prompt} with api key {self.api_key} and path {path}"
        )
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={"authorization": f"Bearer {self.api_key}", "accept": "image/*"},
            files={"none": ""},
            data={
                "prompt": prompt,
                "output_format": "jpeg",
                "aspect_ratio": "16:9",
                "style_preset": style_preset,
                # "negative_prompt": "a dark and stormy night",
                # "seed": 123456, # for consistency
            },
        )

        if response.status_code == 200:
            with open(path, "wb") as file:
                file.write(response.content)
        else:
            raise Exception(str(response.json()))


# Usage:
# generator = ImageGenerator("sk-MYAPIKEY")
# generator.run()
