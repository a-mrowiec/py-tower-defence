"""
Utils
"""
import pygame
from pygame.math import Vector2


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def half_size_of_rect(rect):
    """
    Returns rect with half width and height
    :param rect:
    :return:
    """
    return Vector2(rect.width / 2.0, rect.height / 2.0)
