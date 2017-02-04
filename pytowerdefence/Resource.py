"""
Resources module
"""
import json
import os

import pygame
import pyganim


class ResourceClass:
    """
    Represents resource class
    """
    PHYSICALS = os.path.join('data', 'physicals')
    UI = os.path.join('data', 'ui')
    BULLETS = os.path.join('data', 'physicals', 'bullets')
    CHARACTERS = os.path.join('data', 'physicals', 'characters')


class ResourceManager:
    """
    Manages any resource
    """

    @classmethod
    def load_image(cls, resource_class, name):
        """
        Load image
        :param resource_class:
        :param name:
        :return:
        """
        resource_path = cls.get_path(resource_class, name)
        return pygame.image.load(resource_path)

    @classmethod
    def get_path(cls, resource_class, name):
        """
        Get load path to specific resource
        :param resource_class:
        :param name:
        :return:
        """
        return os.path.join(resource_class, name)

    @classmethod
    def load_animation(cls, resource_class, name):
        """
        Loads animation
        :param resource_class:
        :param name:
        :return:
        """
        with open(cls.get_path(resource_class, name)) as file_data:
            data = json.load(file_data)
            image_path = cls.get_path(resource_class, data["image"])

            if "rects" in data:
                rects = list(map(tuple, data["rects"]))
                images = pyganim.getImagesFromSpriteSheet(image_path,
                                                          rects=rects)
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
