import badp
from pathlib import Path

file_path = Path('exemple.bad')

badp_file = badp.AgendaFile(file_path)

for key in badp_file.data:
    if isinstance(badp_file.data[key], dict):
        for date in badp_file.data[key]:
            print(badp_file.data[key][date].get_image())
    else:
        for item in badp_file.data[key]:
            print(item.get_image())