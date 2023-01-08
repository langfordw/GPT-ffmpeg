#!/opt/homebrew/bin/python3
import argparse
import openai
import subprocess
import os
import json
import re
import shlex

def load_config():
    """
    Load the configuration from a JSON file.
    """
    with open("/usr/local/bin/config.json") as f:
        config = json.load(f)
    return config

# Replace YOUR_API_KEY with your actual API key
openai.api_key = load_config()["api_key"]

def generate_completion(prompt, input_file):
    """
    Use the OpenAI Completion API to generate a completion for the given prompt.
    """
    model_engine = "text-davinci-003"
    prompt = (f"Genearate an ffmpeg prompt in response to a request below. Do not respond with anything other than the ffmpeg command itself. Name the output file 'output' with the relvant extension.\n\nRequest:{prompt}\n\nffmpeg -i {input_file}"
             )

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.0,
    )

    message = completions.choices[0].text
    return message

def validate_command(command):
    """
    Validate an FFmpeg command to ensure that it does not contain any malicious code.
    """
    # Patterns to search for
    patterns = [
        r"rm -rf",  # common Linux command for deleting files and directories recursively
        r"wget",  # command for downloading files from the internet
        r"curl",  # command for transferring data from a server
        r"python -c",  # command for running a Python script from the command line
        r"perl -e",  # command for running a Perl script from the command line
        r"bash -c",  # command for running a Bash script from the command line
        r"&&",  # command for running a Bash script from the command line
    ]
    
    # Check if any of the patterns are present in the command
    for pattern in patterns:
        if re.search(pattern, command):
            return False
    
    # If none of the patterns were found, return True
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str, help="prompt to use for generating completion")
    parser.add_argument("input_file", type=str, help="input file path")
    args = parser.parse_args()

    # Generate a completion using the OpenAI Completion API
    completion = generate_completion(args.prompt, args.input_file)
    completion = completion.replace('output.','"'+os.path.abspath('.')+'/output.')
    command = 'ffmpeg -i "'+os.path.abspath(args.input_file)+'"'+completion+'"'
    print(command)
    
    if (validate_command(command)):
        # Run the FFmpeg command using subprocess
        subprocess.run(command, shell=True)
    else:
        print("Potentially harmful command generated. Aborting.")

if __name__ == "__main__":
    main()
