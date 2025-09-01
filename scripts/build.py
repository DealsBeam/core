import os
import re

# Define file paths
SRC_DIR = 'src'
DIST_DIR = 'dist'
HTML_FILE = os.path.join(SRC_DIR, 'html', 'main.html')
CSS_FILE = os.path.join(SRC_DIR, 'css', 'style.css')
OUTPUT_FILE = os.path.join(DIST_DIR, 'theme.xml')

def parse_theme_variables(css_content):
    """Parses special comments in CSS for theme variable definitions."""
    variable_pattern = re.compile(
        r'/\*\s*@variable\s+'
        r'name="([^"]+)"\s+'
        r'group="([^"]+)"\s+'
        r'type="([^"]+)"\s+'
        r'default="([^"]+)"\s*\*/'
    )
    variables = []
    for match in variable_pattern.finditer(css_content):
        variables.append({
            "name": match.group(1),
            "group": match.group(2),
            "type": match.group(3),
            "default": match.group(4),
        })
    return variables

def generate_variable_tags(variables):
    """Generates <b:variable> XML tags from parsed variable data."""
    tags = []
    for var in variables:
        # The 'value' is set to the 'default' initially.
        tag = f'<b:variable name="{var["name"]}" description="{var["name"]}" group="{var["group"]}" type="{var["type"]}" default="{var["default"]}" value="{var["default"]}"/>'
        tags.append(tag)
    return '\n  '.join(tags)

def create_build_script():
    """
    Reads source files, processes them, and builds the final Blogspot theme XML.
    """
    # Ensure the output directory exists
    os.makedirs(DIST_DIR, exist_ok=True)

    # Read the source HTML and CSS content
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            css_content = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure source files exist.")
        return

    # Define the Blogspot widget structure for blog posts
    blog_posts_widget = """
<b:section class='main' id='main-content' showaddelement='yes'>
  <b:widget id='Blog1' locked='true' title='Blog Posts' type='Blog' version='2'>
    <b:includable id='main'>
      <b:loop values='data:posts' var='post'>
        <article>
          <h2><a expr:href='data:post.url'><data:post.title/></a></h2>
          <p class='post-meta'>Published on <data:post.timestamp/></p>
          <div class='post-body'>
            <data:post.body/>
          </div>
        </article>
      </b:loop>
    </b:includable>
  </b:widget>
</b:section>
"""

    # Extract only the content within the <body> tag from the source HTML
    body_match = re.search(r'<body[^>]*>((?:.|\n)*)</body>', html_content, re.IGNORECASE)
    if not body_match:
        print("Error: Could not find <body> content in html/main.html")
        return
    body_content = body_match.group(1).strip()

    # Replace the HTML placeholder loop with the actual Blogspot widget
    body_content = re.sub(
        r'<!--\s*POSTS_LOOP_START\s*-->(?:.|\n)*?<!--\s*POSTS_LOOP_END\s*-->',
        blog_posts_widget,
        body_content
    )

    # Define the valid header section with the widget nested inside
    header_section = """
<b:section class='header' id='header' maxwidgets='1' showaddelement='no'>
  <b:widget id='Header1' locked='true' title='Blog Title' type='Header' version='2'>
    <b:includable id='main'>
      <div class='header-inner'>
        <h1><a expr:href='data:blog.homepageUrl'><data:title/></a></h1>
        <p><data:description/></p>
      </div>
    </b:includable>
  </b:widget>
</b:section>
"""
    # Replace the header placeholder with the valid section
    body_content = body_content.replace('<!-- HEADER_SECTION -->', header_section)

    # Generate <b:variable> tags from CSS comments
    variables = parse_theme_variables(css_content)
    variable_tags = generate_variable_tags(variables)

    # Define the final XML theme structure
    xml_template = f"""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html>
<html b:version='2' class='v2' expr:dir='data:blog.languageDirection' xmlns='http://www.w3.org/1999/xhtml' xmlns:b='http://www.google.com/2005/gml/b' xmlns:data='http://www.google.com/2005/gml/data' xmlns:expr='http://www.google.com/2005/gml/expr'>
<head>
  <meta charset='UTF-8'/>
  <meta content='width=device-width, initial-scale=1.0' name='viewport'/>
  <title><data:blog.pageTitle/></title>
  <b:if cond='true'>
    {variable_tags}
  </b:if>
  <b:skin><![CDATA[
{css_content}
  ]]></b:skin>
</head>
<body>
{body_content}
</body>
</html>
"""

    # Write the completed template to the output file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_template)

    print(f"Theme successfully built at '{OUTPUT_FILE}'")

if __name__ == '__main__':
    create_build_script()
