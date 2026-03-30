import re
from unidecode import unidecode



def create_slug(category):
    if re.search(" ", category):
        slug = unidecode(category.lower().strip())
        # Remove unwanted punctuation: parentheses, commas, periods
        slug = re.sub(r"[()\[\],.?&']", "", slug)
        # Replace spaces with underscores
        slug = slug.replace(" ", "_")
        # Collapse multiple dashes (--- or --) into a single dash
        slug = re.sub(r"-{2,}", "-", slug)

    else:
        slug = unidecode(category.lower().strip())
        # Remove unwanted punctuation: parentheses, commas, periods
        slug = re.sub(r"[()\[\],.?&']", "", slug)
        # Collapse multiple dashes (--- or --) into a single dash
        slug = re.sub(r"-{2,}", "-", slug)

    return slug

 