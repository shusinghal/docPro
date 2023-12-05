from flask import Flask, request, render_template, jsonify, g
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import requests
import os
import git
import zipfile

app = Flask(__name__)

# Initialize global variables
g.double_spaces_count = 0
g.broken_links = []


@app.route('/', methods=['GET', 'POST'])
def analyze_repo():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('templates', filename)

            if os.path.exists(file_path):
                # Delete the file
                os.remove(file_path)

            # Save the file
            file.save(file_path)

            if filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall('templates', overwrite=True)

            process_file_or_repo(filename)

            return render_template('result.html', count=g.double_spaces_count, broken_links=g.broken_links)

    if request.method == 'GET':
        return render_template('upload.html')

@app.route('/data', methods=['GET'])
def get_data():
    data = {
        'double_spaces_count': g.double_spaces_count,
        'broken_links_count': len(g.broken_links)
    }
    return jsonify(data)

@app.route('/correct_double_spaces', methods=['POST'])
def correct_double_spaces():
    global filename

    try:
        with open(os.path.join('templates', filename), 'r') as f:
            content = f.read()

        # Remove double spaces
        content = content.replace('  ', ' ')

        with open(os.path.join('templates', filename), 'w') as f:
            f.write(content)

        # Recount double spaces after correction
        g.double_spaces_count = 0
        process_file_or_repo(filename)

        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False})

def process_file_or_repo(filename):
    if filename.endswith('.txt'):
        process_file(filename)
    else:
        process_repo(filename)

def process_file(filename):
    file_path = os.path.join('templates', filename)
    with open(file_path, 'r') as f:
        content = f.read()

    count_double_spaces(content)
    check_broken_links(content)

def process_repo(repo_name):
    repo_dir = os.path.join('repos', repo_name)

    if not os.path.exists(repo_dir):
        git.Repo.clone_from(f'https://github.com/{repo_name}', repo_dir)

    for foldername, subfolders, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith('.txt'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r') as f:
                    content = f.read()

                count_double_spaces(content)
                check_broken_links(content)

def count_double_spaces(content):
    lines = content.split('\n')
    g.double_spaces_count += sum(line.count('  ') for line in lines)

def check_broken_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                g.broken_links.append(url)
        except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects):
            g.broken_links.append(url)

if __name__ == '__main__':
    app.run(debug=True)

