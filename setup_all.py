import os
import re
import json

output = os.popen("pulumi up --skip-preview").read()

split_output = output.splitlines()
# Extract outputs from pulumi file
config = split_output[
    split_output.index('Outputs:')+1:
    split_output.index('Resources:')-1]

#Clean outputs and save to json file
config = [re.sub(" +|\"", "", item) for item in config]
config = {pair[0]:pair[1] for pair in [item.split(":") for item in config]}
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)