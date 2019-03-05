import json
from json import dump,loads
data_file = ""

with open('static/data_file.json', 'r') as f:
    data_file_to_clean = json.load(f)

for entity in data_file_to_clean:
    data_file = entity


f = open("static/data_file.json", "w")
dump(data_file,f, indent=4)
f.close()