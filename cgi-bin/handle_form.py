#!/usr/bin/env python3
import cgi
import cgitb
import subprocess
import yaml
import os

# Enable error reporting
cgitb.enable()

# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Define the path to the YAML configuration file
yaml_config_path = os.path.join(script_dir, 'linkedinconfig.yaml')

# Check if the form was submitted
form = cgi.FieldStorage()
if form:  # Form was submitted, so process the data
    # Update the YAML file with the form data
    config_data = {key: form.getvalue(key) for key in form.keys()}
    with open(yaml_config_path, 'w') as yaml_file:
        yaml.dump(config_data, yaml_file, default_flow_style=False)

    # Run the main.py script
    # Ensure the path points to the correct location of main.py
    subprocess.run(["python3", "/Users/James/Desktop/AutoApply-main/main.py"])

    # Provide feedback to the user
    print("Content-Type: text/html\n")  # HTML is following

