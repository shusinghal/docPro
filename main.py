from flask import Flask, request, render_template, jsonify, g
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import requests
import os
import git
import zipfile

app = Flask(__name__)

@app.before_request
def before_request():
    g.double_spaces_count = 0
    g.broken_links = []
    g.report_dir = ''
    #return (double_spaces_count)
# Initialize global variables

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
                    zip_ref.extractall('teamplates', overwrite = True)
            g.double_spaces_count = 0
            broken_links = []
            
            # Walk through all the files in the repository
            for foldername, subfolders, filenames in os.walk('templates'):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    
                    # Only analyze text files
                    if filename.endswith(('.txt', '.json', '.xml', '.svg', '.pdf', '.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp', '.epub')):
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        lines = content.split('\n')
                        g.double_spaces_count += sum(line.count('  ') for line in lines)
                        print(f"double spaces count is {double_spaces_count}")
                        soup = BeautifulSoup(content, 'html.parser')
                        for link in soup.find_all('a'):
                            url = link.get('href')
                            try:
                                response = requests.head(url, timeout=5)
                                if response.status_code != 200:
                                    g.broken_links.append(url)
                            except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects):
                                broken_links.append(url)
            
            return render_template('result.html', count=g.double_spaces_count, broken_links=g.broken_links)
        if request.method == 'POST':
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
                    
                    double_spaces_count = 0
                    broken_links = []
                    
                    # Walk through all the files in the repository
                    for foldername, subfolders, filenames in os.walk(repo_dir):
                        for filename in filenames:
                            file_path = os.path.join(foldername, filename)
                            
                            # Only analyze text files
                            if filename.endswith('.txt'):
                                with open(file_path, 'r') as f:
                                    content = f.read()
                                
                                lines = content.split('\n')
                                double_spaces_count += sum(line.count('  ') for line in lines)
                                print(f"double spaces count 2 is {double_spaces_count}")
                                soup = BeautifulSoup(content, 'html.parser')
                                for link in soup.find_all('a'):
                                    url = link.get('href')
                                    try:
                                        response = requests.head(url, timeout=5)
                                        if response.status_code != 200:
                                            broken_links.append(url)
                                    except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects):
                                        broken_links.append(url)
                    
                    return render_template('result.html', double_spaces_count=double_spaces_count, broken_links=broken_links)
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
    global double_spaces_count, filename
    try:
        with open(os.path.join('templates', filename), 'r') as f:
            content = f.read()
        
        content = content.replace('  ', ' ')
        
        with open(os.path.join('templates', filename), 'w') as f:
            f.write(content)
        
        double_spaces_count = content.count('  ')
        
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False})
if __name__ == '__main__':
    app.run(debug=True)
