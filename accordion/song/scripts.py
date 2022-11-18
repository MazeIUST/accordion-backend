from .models import Tag
from .const import *


def create_tag():
    tags = []
    for tag in TAGS:
        if not Tag.objects.filter(name=tag).exists():
            new_tag = Tag(name=tag)
            tags.append(new_tag)
    return Tag.objects.bulk_create(tags)