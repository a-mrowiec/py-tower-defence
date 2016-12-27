import pygame


class Actor(pygame.sprite.Sprite):
    _position = [0, 0]
    _prev_position = [0, 0]
    _velocity = [0, 0]
    rect = pygame.Rect(0, 0, 0, 0)
    animation = None

    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)

    def update(self, dt):
        self._prev_position = self._position[:]
        self._position[0] += self._velocity[0] * dt
        self._position[1] += self._velocity[1] * dt
        self.rect.center = self._position
        if self.animation is not None:
            self.image = self.animation.getCurrentFrame()

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self.velocity = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.rect.center = self._position


import pyganim

rects = [(  0, 154, 94, 77),
         ( 94, 154, 94, 77),
         (188, 154, 94, 77),
         (282, 154, 94, 77),
         (376, 154, 94, 77),
         (470, 154, 94, 77),
         (564, 154, 94, 77),
         (658, 154, 94, 77),
         (752, 154, 94, 77),]


class TestAnimatedActor(Actor):
    def __init__(self):
        super().__init__()
        allImages = pyganim.getImagesFromSpriteSheet('data/terrex_0.png', rects=rects)
        frames = list(zip(allImages, [100] * len(allImages)))

        self.animation = pyganim.PygAnimation(frames)
        self.animation.play() # there is also a pause() and stop() method