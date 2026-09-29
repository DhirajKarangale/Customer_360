import os
import glob

for f in glob.glob('backend/**/*.py', recursive=True):
    with open(f, 'r') as file:
        content = file.read()
    
    new_content = content.replace('server.', 'backend.').replace('from server ', 'from backend ').replace('import server', 'import backend').replace('"server.main:app"', '"backend.main:app"')
    
    if new_content != content:
        with open(f, 'w') as file:
            file.write(new_content)
