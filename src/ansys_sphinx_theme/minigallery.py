# Parse the api reference and examples from theme options and render mini gallery
# read the thumbnail images from the examples


def get_thumbnail_images_from_examples(examples):
    """Extract thumbnail images from example definitions."""
    thumbnails = []
    for example in examples:
        thumbnail = example.get("thumbnail", "")
        if thumbnail:
            thumbnails.append(thumbnail)
    return thumbnails


def generate_minigallery(app, pagename, templatename, context, doctree):
    """Generate mini gallery from theme options."""
    if "theme_options" not in context:
        return

    theme_options = context["theme_options"]
    if "minigallery" not in theme_options:
        return

    minigallery = theme_options["minigallery"]
    if not minigallery.get("enabled", False):
        return

    # Get the examples from the theme options
    examples = minigallery.get("examples", [])
    if not examples:
        return

    # Generate the HTML for the mini gallery
    gallery_html = '<div class="minigallery">\n'
    for example in examples:
        title = example.get("title", "Example")
        description = example.get("description", "")
        thumbnail = example.get("thumbnail", "")
        link = example.get("link", "#")

        gallery_html += f'  <div class="minigallery-item">\n'
        gallery_html += f'    <a href="{link}">\n'
        if thumbnail:
            gallery_html += f'      <img src="{thumbnail}" alt="{title} thumbnail"/>\n'
        gallery_html += f'      <h3>{title}</h3>\n'
        if description:
            gallery_html += f'      <p>{description}</p>\n'
        gallery_html += f'    </a>\n'
        gallery_html += f'  </div>\n'

    gallery_html += '</div>\n'

    # Inject the mini gallery HTML into the page context
    context["minigallery_html"] = gallery_html