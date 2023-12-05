import re
import requests
import pandas as pd
import matplotlib.pyplot as plt

def parse_text_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text

def find_double_spaces(text):
    matches = re.findall(r'\b\w+\s{2,}\w+\b', text)
    return matches

def calculate_readability_score(text):
    words = re.findall(r'\b\w+\b', text)
    num_words = len(words)
    num_sentences = text.count('.') + text.count('!') + text.count('?')
    num_syllables = sum([count_syllables(word) for word in words])

    readability_score = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    return readability_score

def count_syllables(word):
    vowels = 'aeiouy'
    num_syllables = 0
    prev_char = None
    for char in word:
        if char in vowels and prev_char not in vowels:
            num_syllables += 1
        prev_char = char
    if word.endswith('e'):
        num_syllables -= 1
    if num_syllables == 0:
        num_syllables = 1
    return num_syllables

def count_broken_links(url):
    response = requests.get(url)
    links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)

    broken_links = 0
    for link in links:
        if not link.startswith('http'):
            link = url + link
        try:
            link_response = requests.head(link)
            if link_response.status_code >= 400:
                broken_links += 1
        except requests.exceptions.RequestException:
            broken_links += 1

    return broken_links

# Example usage
file_path = 'example.txt'
text = parse_text_file(file_path)
double_spaces = find_double_spaces(text)
readability_score = calculate_readability_score(text)

url = 'https://example.com'
broken_links = count_broken_links(url)

# Create a dashboard
df = pd.DataFrame({'Double Spaces': double_spaces, 'Broken Links': [broken_links]})
fig, ax = plt.subplots(figsize=(8, 6))
ax.axis('off')
ax.table(cellText=df.values, colLabels=df.columns, loc='center')
plt.title('Double Spaces and Broken Links')
plt.show()