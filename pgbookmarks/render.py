import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pgbookmarks import logger


STARTPAGE_FILENAME = 'startpage.html'


def GetStartpageString(bookmark_collection, templates_path,
                       template_name='template.jinja'):

    env = Environment(loader=FileSystemLoader(templates_path),
                      autoescape=select_autoescape(['html']))

    template = env.get_template(template_name)

    html = template.render({'bookmark_collection': bookmark_collection})
    return html


def WriteStartpageFile(html, output_directory):

    os.makedirs(output_directory, exist_ok=True)

    target_path = os.path.join(output_directory, STARTPAGE_FILENAME)

    with open(target_path, 'w') as html_output_file:
        print(html, file=html_output_file)


def CopyStaticFiles(static_directory, output_directory):
    for file in os.listdir(static_directory):
        shutil.copy(os.path.join(static_directory, file), output_directory)
