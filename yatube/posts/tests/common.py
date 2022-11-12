from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'small.gif') -> SimpleUploadedFile:
    small_gif = Image.new(
        'RGBA',
        size=(50, 50),
        color=(155, 0, 0),
    )
    return SimpleUploadedFile(
        name=name,
        content=small_gif,
        content_type='image/gif',
    )
