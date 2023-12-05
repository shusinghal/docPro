import os
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import git
import requests

app = Flask(__name__)

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
            results.append((file.filename, double_spaces, broken_links, len(broken_links)))
        return render_template('result.html', results=results)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
