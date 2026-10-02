import glob
import re
import os

files = glob.glob('src/**/*.jsx', recursive=True) + glob.glob('src/**/*.js', recursive=True)
for file in files:
    if file.endswith('useAuth.js'):
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'useAuth' in content:
        new_content = re.sub(r"from (['\"])(.*?)/?AuthContext(['\"])", r"from \1\2/useAuth\3", content)
        if new_content != content:
            print('Updated', file)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
