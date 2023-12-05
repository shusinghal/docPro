import os
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import git
import requests
import re

app = Flask(__name__)
def calculate_ari(content):
    sentences = re.split(r'[.!?]', content)
    words = re.split(r'\s', content)
    characters = [c for c in content if c.isalpha()]
    
    # Check if sentences and words are not empty to avoid division by zero
    if len(words) > 0 and len(sentences) > 0:
        ari = 4.71 * (len(characters)/len(words)) + 0.5 * (len(words)/len(sentences)) - 21.43
        ari = round(ari, 2)
        if ari < 1:
            readability_level = "Kindergarten"
        elif ari < 2:
            readability_level = "First/Second Grade"
        elif ari < 3:
            readability_level = "Third Grade"
        elif ari < 4:
            readability_level = "Fourth Grade"
        elif ari < 5:
            readability_level = "Fifth Grade"
        elif ari < 6:
            readability_level = "Sixth Grade"
        elif ari < 7:
            readability_level = "Seventh Grade"
        elif ari < 8:
            readability_level = "Eighth Grade"
        elif ari < 9:
            readability_level = "Ninth Grade"
        elif ari < 10:
            readability_level = "Tenth Grade"
        elif ari < 11:
            readability_level = "Eleventh Grade"
        elif ari < 12:
            readability_level = "Twelfth grade"
        elif ari < 13:
            readability_level = "College student"
        else:
            readability_level = "Professor"
        return ari, readability_level
    else:
        return "Not enough data to calculate ARI"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        url = request.form['url']

        if url:
                # Extract the repository name from the URL and use it as the directory name
                repo_name = url.rsplit('/', 1)[-1]
                if '.git' in repo_name:
                    repo_name = repo_name[:-4]
                repo_dir = os.path.join('repos', repo_name)
                
                # Only clone the repository if it hasn't been cloned already
                if not os.path.exists(repo_dir):
                    git.Repo.clone_from(url, repo_dir)
                for root, _, filenames in os.walk(repo_dir):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
        results = []
        # Check for double spaces
        for file in files:
            content = file.read().decode('utf-8')
            
            lines = content.split('\n')
            double_spaces = sum(line.count('  ') for line in lines)
            #double_spaces = content.count('  ')

            # Check for broken links
            soup = BeautifulSoup(content, 'html.parser')
            broken_links = []
            for link in soup.find_all('a'):
                url = link.get('href')
                try:
                    response = requests.head(url, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append(url)
                except requests.exceptions.RequestException:
                    broken_links.append(url)
            # Check ARI
            ari, readability_level = calculate_ari(content)
            results.append((file.filename, double_spaces, broken_links, len(broken_links), ari, readability_level))
        return render_template('result.html', results=results)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
