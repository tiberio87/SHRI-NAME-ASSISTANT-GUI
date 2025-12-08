import os

basename = 'Movie.2024.1080p.BluRay.x264-DDNCREW'
name_no_ext = os.path.splitext(basename)[0]
print(f'basename: {basename}')
print(f'name_no_ext: {name_no_ext}')
has_hyphen = '-' in name_no_ext
print(f'Has hyphen: {has_hyphen}')
if '-' in name_no_ext:
    parts = name_no_ext.rsplit('-', 1)
    print(f'Parts: {parts}')
    print(f'Release group candidate: {parts[1]}')
