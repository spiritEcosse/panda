from slugify import slugify as python_slugify

def slugify(value, **kwargs):
    return python_slugify(value)
