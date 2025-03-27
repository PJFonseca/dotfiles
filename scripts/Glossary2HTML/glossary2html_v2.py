import subprocess
import sys
import pandas as pd
import re
from jinja2 import Template

# Function to install a package if missing
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure required packages are installed
for package in ["pandas", "jinja2"]:
    install_package(package)

# Load the glossary CSV
csv_file = "glossary.csv"  # Ensure this file exists
df = pd.read_csv(csv_file)

# Ensure required columns exist
expected_columns = ['Title', 'Acronym', 'Description', 'Last Updated']
for col in expected_columns:
    if col not in df.columns:
        print(f"Error: Missing column '{col}' in CSV. Found: {df.columns.tolist()}")
        sys.exit(1)

# Keep only relevant columns
df = df[['Title', 'Acronym', 'Description', 'Last Updated']]

# Ensure 'Title' and 'Acronym' are strings, replacing NaN with an empty string
df['Title'] = df['Title'].astype(str)
df['Acronym'] = df['Acronym'].fillna("").astype(str)

# Generate URL-friendly anchors
def create_link(name):
    return "#" + re.sub(r'\W+', '_', name).strip('_')

df['title_link'] = df['Title'].apply(create_link)
df['acronym_link'] = df.apply(lambda row: create_link(row['Acronym']) if row['Acronym'] else "", axis=1)

# Create a mapping for linking terms
title_to_link = {row['Title'].lower(): row['title_link'] for _, row in df.iterrows()}
acronym_to_title = {row['Acronym']: row['Title'] for _, row in df.iterrows() if row['Acronym']}
acronym_to_link = {row['Acronym'].lower(): row['acronym_link'] for _, row in df.iterrows() if row['Acronym']}

# Function to replace terms with links in descriptions
def linkify_description(description, title_to_link, acronym_to_link, acronym_to_title, current_title):
    def replace_match(match):
        term = match.group(0)
        lower_term = term.lower()
        
        # Skip linking if the term is its own title
        if lower_term == current_title.lower():
            return term
        
        if lower_term in title_to_link:
            return f'<a href="{title_to_link[lower_term]}">{term}</a>'
        if lower_term in acronym_to_link:
            title = acronym_to_title.get(term, term)  # Get the full title for display
            return f'<a href="{acronym_to_link[lower_term]}">{title} ({term})</a>'
        return term

    # Ensure full word matching using word boundaries `\b`
    pattern = r'\b(' + '|'.join(map(re.escape, set(title_to_link) | set(acronym_to_link))) + r')\b'
    return re.sub(pattern, replace_match, description, flags=re.IGNORECASE)

# Apply linkifying function to descriptions
df['Description'] = df.apply(lambda row: linkify_description(row['Description'], title_to_link, acronym_to_link, acronym_to_title, row['Title']), axis=1)

# Sort by first letter and title
df['first_letter'] = df['Title'].str[0].str.upper()
df_sorted = df.sort_values(by=['first_letter', 'Title'])

# Group by first letter
grouped_terms = df_sorted.groupby('first_letter')

# Jinja2 HTML template
template_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Glossary</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .entry { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #ddd; }
        .title { font-weight: bold; font-size: 18px; }
        .acronym { font-size: 14px; color: gray; }
        .description { margin-top: 5px; }
        .date { font-size: 12px; color: gray; }
        .letter-group { margin-top: 30px; font-size: 24px; font-weight: bold; border-bottom: 2px solid black; padding-bottom: 5px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Glossary</h1>
    {% for letter, entries in glossary.items() %}
        <div class="letter-group">{{ letter }}</div>
        {% for entry in entries %}
            <div class="entry" id="{{ entry.title_link[1:] }}">
                <div class="title">
                    <a href="{{ entry.title_link }}">{{ entry.Title }}</a>
                </div>
                {% if entry.Acronym %}
                    <div class="acronym" id="{{ entry.Acronym }}">
                        (<a href="{{ entry.acronym_link }}">{{ entry.Acronym }}</a>)
                    </div>
                {% endif %}
                <div class="description">{{ entry.Description | safe }}</div>
                {% if entry['Last Updated'] and entry['Last Updated'] != 'nan' %}
                    <div class="date">Last Updated: {{ entry['Last Updated'] }}</div>
                {% endif %}
            </div>
        {% endfor %}
    {% endfor %}
</body>
</html>
"""

# Render HTML
glossary_dict = {letter: entries.to_dict(orient='records') for letter, entries in grouped_terms}
template = Template(template_html)
html_output = template.render(glossary=glossary_dict)

# Save the HTML file
html_file = "glossary.html"
with open(html_file, "w", encoding="utf-8") as file:
    file.write(html_output)

print(f"Glossary HTML generated successfully: {html_file}")
