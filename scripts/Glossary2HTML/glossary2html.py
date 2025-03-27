import subprocess
import sys

# Function to install a package if it's missing
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure required packages are installed
for package in ["pandas", "numpy", "jinja2"]:
    install_package(package)

import pandas as pd
import re
from jinja2 import Template

# Load the glossary CSV
csv_file = "glossary.csv"  # Ensure this file exists in the same directory
df = pd.read_csv(csv_file)

# Ensure column names match exactly
df = df[['title', 'description', 'last_updated']]

# Create a dictionary of titles to URLs (assume lowercase for matching)
title_to_link = {row['title'].lower(): f"#{row['title'].replace(' ', '_')}" for _, row in df.iterrows()}

# Function to replace glossary terms with links in descriptions
def linkify_description(description, title_to_link):
    def replace_match(match):
        term = match.group(0)
        link = title_to_link.get(term.lower())
        return f'<a href="{link}">{term}</a>' if link else term

    # Create regex pattern for all glossary terms
    pattern = r'\b(' + '|'.join(re.escape(title) for title in title_to_link.keys()) + r')\b'
    return re.sub(pattern, replace_match, description, flags=re.IGNORECASE)

# Apply linkify function to descriptions
df['description'] = df['description'].apply(lambda desc: linkify_description(desc, title_to_link))

# Jinja2 HTML template
template_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Glossary</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .entry { margin-bottom: 20px; }
        .title { font-weight: bold; font-size: 18px; }
        .description { margin-top: 5px; }
        .date { font-size: 12px; color: gray; }
    </style>
</head>
<body>
    <h1>Glossary</h1>
    {% for entry in glossary %}
        <div class="entry" id="{{ entry.title.replace(' ', '_') }}">
            <div class="title">{{ entry.title }}</div>
            <div class="description">{{ entry.description | safe }}</div>
            <div class="date">Last Updated: {{ entry.last_updated }}</div>
        </div>
    {% endfor %}
</body>
</html>
"""

# Render HTML
template = Template(template_html)
html_output = template.render(glossary=df.to_dict(orient='records'))

# Save the HTML file
html_file = "glossary.html"
with open(html_file, "w", encoding="utf-8") as file:
    file.write(html_output)

print(f"Glossary HTML generated successfully: {html_file}")
