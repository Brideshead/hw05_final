from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    file = BytesIO()
    image = Image.new(
        'RGBA',
        size=(50, 50),
        color=(155, 0, 0),
    )
    image.save(file, 'gif')
    file.name = 'small.gif'
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file,
        content_type='image/gif',
    )
