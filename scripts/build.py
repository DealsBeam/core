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
<b:tag cond='data:view.isLayoutMode' name='div' class='layout-section'>
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
          <div class='post-footer'>
            <div class='post-labels'>
              <b:if cond='data:post.labels'>
                <span class='post-labels-title'>Labels:</span>
                <b:loop values='data:post.labels' var='label'>
                  <a expr:href='data:label.url' rel='tag'><data:label.name/></a><b:if cond='data:label.isLast != "true"'>, </b:if>
                </b:loop>
              </b:if>
            </div>
            <div class='post-share-buttons'>
                <a class='share-twitter' expr:href='&quot;https://twitter.com/intent/tweet?text=&quot; + data:post.title + &quot;&amp;url=&quot; + data:post.url' target='_blank'>Share on Twitter</a>
                <a class='share-facebook' expr:href='&quot;https://www.facebook.com/sharer/sharer.php?u=&quot; + data:post.url' target='_blank'>Share on Facebook</a>
                <a class='share-email' expr:href='&quot;mailto:?subject=&quot; + data:post.title + &quot;&amp;body=&quot; + data:post.url' target='_blank'>Share via Email</a>
            </div>
          </div>
          <b:if cond='data:post.allowComments'>
            <b:include data='post' name='postComments'/>
          </b:if>
        </article>
      </b:loop>
      <b:include name='nextprev'/>
    </b:includable>
    <b:includable id='nextprev'>
      <div class='pagination'>
        <b:if cond='data:newerPageUrl'>
          <a class='pagination-newer' expr:href='data:newerPageUrl'>&#171; Newer Posts</a>
        </b:if>
        <b:if cond='data:olderPageUrl'>
          <a class='pagination-older' expr:href='data:olderPageUrl'>Older Posts &#187;</a>
        </b:if>
      </div>
    </b:includable>
    <b:includable id='postComments' var='post'>
      <div class='comments' id='comments'>
        <b:if cond='data:post.allowComments'>
          <b:if cond='data:post.numComments != 0'>
            <h4><data:post.numComments/> Comments:</h4>
          </b:if>
          <div id='comments-block'>
            <b:loop values='data:post.comments' var='comment'>
              <div class='comment'>
                <div class='comment-author'>
                  <b:if cond='data:comment.authorUrl'>
                    <a expr:href='data:comment.authorUrl' rel='nofollow'><data:comment.author/></a>
                  <b:else/>
                    <data:comment.author/>
                  </b:if>
                </div>
                <div class='comment-body'>
                  <p><data:comment.body/></p>
                </div>
              </div>
            </b:loop>
          </div>
        </b:if>
        <div class='comment-form'>
          <b:if cond='data:post.embedCommentForm'>
            <b:include data='post' name='comment-form'/>
          <b:else/>
            <a expr:href='data:post.addCommentUrl' target='_blank'>Post a Comment</a>
          </b:if>
        </div>
      </div>
    </b:includable>
  </b:widget>
</b:section>
</b:tag>
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
<b:tag cond='data:view.isLayoutMode' name='div' class='layout-section'>
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
</b:tag>
"""
    # Replace the header placeholder with the valid section
    body_content = body_content.replace('<!-- HEADER_SECTION -->', header_section)

    # Define the sidebar section
    sidebar_section = """
<b:tag cond='data:view.isLayoutMode' name='div' class='layout-section'>
  <b:section class='sidebar' id='sidebar' showaddelement='yes'>
  </b:section>
</b:tag>
"""
    # Replace the sidebar placeholder
    body_content = body_content.replace('<!-- SIDEBAR_SECTION -->', sidebar_section)

    admin_css_content = """body#layout{background-color:#f4f4f5;padding:14px}body#layout .layout-section{float:left;min-width:386px;margin:0 16px 16px 0}body#layout .layout-widget-description{display:none}body#layout .Blog .widget-content{height:auto}body#layout .widget-wrap3{border-bottom:1px solid #f2f2f2;overflow:hidden}body#layout .draggable-widget .widget-wrap3{background:0 0;margin-left:0}body#layout .draggable-widget .widget-wrap2{cursor:default;background:0 0}body#layout .widget .editlink.icon{background-image:none;width:100%;height:100%;top:0;left:0}body#layout .widget.el_active{margin:0}body#layout .widget.el_active .editlink.icon{display:none}body#layout .dr_active{border:1px dashed #ccc;margin:0}body#layout .AdSense .layout-title:before{content:"AdSense: "}body#layout .HTML .layout-title:before{content:"HTML: "}body#layout .Header .layout-title:before{content:"Header: "}body#layout .Text .layout-title:before{content:"Text: "}body#layout .TextList .layout-title:before{content:"TextList: "}body#layout .Blog .layout-title:before{content:"Blog: "}body#layout .BlogSearch .layout-title:before{content:"Search: "}body#layout .BlogArchive .layout-title:before{content:"Archive: "}body#layout .FeaturedPost .layout-title:before{content:"Featured: "}body#layout .PopularPosts .layout-title:before{content:"Populars: "}body#layout .Profile .layout-title:before{content:"Profile: "}body#layout .Image .layout-title:before{content:"Image: "}body#layout .Label .layout-title:before{content:"Label: "}body#layout .PageList .layout-title:before{content:"PageList: "}body#layout .LinkList .layout-title:before{content:"LinkList: "}body#layout .ContactForm .layout-title:before{content:"Contact: "}body#layout .Subscribe .layout-title:before{content:"Subscribe: "}body#layout div.section{background-color:#fff;margin:0 0 16px;padding:12px;height:auto!important}body#layout div.section.activated-section{border-color:#8c8f94}body#layout div.section h4{text-transform:capitalize;color:#263238;margin:0 0 14px;font-size:17px;font-weight:400}body#layout div.section .add_widget{padding:12px}body#layout div.section .add_widget a{color:#263238;margin-left:32px;font-size:14px}body#layout div.section .add_widget a:hover{color:#23a6b3;text-decoration:none}body#layout div.section .widget .widget-content{color:#263238;background-color:#f6f7f7;border:1px solid #c3c4c7;padding:12px}body#layout div.section .widget .widget-content:hover{border-color:#8c8f94}body#layout div.section .widget .widget-content .layout-title{color:#999;margin:0 30px 0 0;font-size:14px}body#layout div.section .widget .widget-content .layout-title:before{color:#262626;font-weight:500}body#layout div.section .widget .layout-widget-state{background-size:cover;width:20px;height:20px;margin-top:2px;margin-right:10px}body#layout div.section .locked-widget .widget-content{background-image:url(https://www.gstatic.com/images/icons/material/system_gm/1x/lock_grey600_24dp.png);background-position:right 10px center;background-repeat:no-repeat;background-size:20px}body#layout .layout-edit .section .widget-content .editlink.icon{background-color:#f1f3f3;background-image:url(https://www.gstatic.com/images/icons/material/system_gm/1x/mode_edit_grey600_24dp.png);background-repeat:no-repeat;background-size:20px;border-left:1px solid #c3c4c7;width:36px;left:auto;right:0}body#layout .layout-edit .section .widget-content .editlink.icon:hover{background-color:#e3e8e8}body#layout .layout-edit .section .widget-content:hover{border-color:#c3c4c7}body#layout .layout-edit .section .widget-content .layout-title{margin:0 58px 0 0}body#layout .layout-edit .section .widget.el_active .editlink.icon{display:block}body#layout .layout-edit .section .locked-widget .widget-content{background-position:right 46px center}"""

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
  <b:template-skin><![CDATA[
{admin_css_content}
  ]]></b:template-skin>
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
