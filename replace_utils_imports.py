import glob

for f in glob.glob('ai/**/*.py', recursive=True):
    with open(f, 'r') as file:
        content = file.read()
    
    new_content = content.replace('from utils.', 'from ai.utils.')
    
    if new_content != content:
        with open(f, 'w') as file:
            file.write(new_content)
