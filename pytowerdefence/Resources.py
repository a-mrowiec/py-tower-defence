import os
import json
import pygame
import pyganim


class ResourceClass:
    PHYSICALS = 'data/physicals'
    UI = 'data/ui'
    BULLETS = 'data/physicals/bullets'
    CHARACTERS = os.path.join('data', 'physicals', 'characters')


class ResourceManager:

    @classmethod
    def load_image(cls, resource_class, name):
        resource_path = cls.get_path(resource_class, name)
        return pygame.image.load(resource_path)

    @classmethod
    def get_path(cls, resource_class, name):
        return os.path.join(resource_class, name)

    @classmethod
    def load_animation(cls, resource_class, name):
        with open(cls.get_path(resource_class, name)) as file_data:
            data = json.load(file_data)
            image_path = cls.get_path(resource_class, data["image"])

            if "rects" in data:
                rects = list(map(lambda a: tuple(a), data["rects"]))
                images = pyganim.getImagesFromSpriteSheet(image_path, rects=rects)
            else:
                rows = data["rows"]
                cols = data["cols"]
                images = pyganim.getImagesFromSpriteSheet(image_path, rows=rows,
                                                          cols=cols, rects=[])
            speed = [data.get('speed', 100)]
            frames = list(zip(images, speed * len(images)))
            animation = pyganim.PygAnimation(frames)
            animation.loop = data.get('loop', True)
            return animation
