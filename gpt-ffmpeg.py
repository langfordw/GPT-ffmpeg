#!/opt/homebrew/bin/python3
import argparse
from openai import OpenAI
import subprocess
import os
import json
import re
from termcolor import colored

client = None

def load_config():
    """
    Load the configuration from a JSON file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    with open(config_path) as f:
        config = json.load(f)
    return config

def generate_completion(prompt, input_file):
    """
    Use the OpenAI Chat Completion API to generate a completion for the given prompt.
    """
    prompt = (
        "Generate an ffmpeg prompt in response to a request below. Do not respond "
        "with anything other than the ffmpeg command itself. Name the output file "
        "'output' with the relvant extension except in the case of a repeated output pattern.\n\n"
        f"Request:{prompt}\n\nffmpeg -i {input_file}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.0,
    )

    message = response.choices[0].message.content
    return message

def fix_command(command, input_prompt):
    """
    Use the OpenAI Chat Completion API to fix an erroneous FFmpeg command.
    """
    # Set the prompt for the Completion API
    prompt = (
        f"Fix the following FFmpeg command. The intended functionality is to {input_prompt}:\n\n{command}\n\nFFmpeg "
    )

    # Use the Chat Completion API to generate a fixed version of the command
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.0,
    )

    fixed = response.choices[0].message.content.strip()
    if not fixed.lower().startswith("ffmpeg"):
        fixed = "ffmpeg " + fixed

    return fixed


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
    parser.add_argument("input_file", type=str, nargs="+", help="input file path(s)")
    args = parser.parse_args()

    # Format input_files string with absolute path
    input_files = " ".join(['-i "'+os.path.abspath(f)+'"' for f in args.input_file])

    # Generate a completion using the OpenAI Completion API
    completion = generate_completion(args.prompt, input_files)

    # Add absolute path to output
    completion = completion.replace('output','"'+os.path.abspath('.')+'/output')

    # Format command
    command = 'ffmpeg '+input_files+' '+completion+'"'

    # Run command back through GPT to correct any errors
    fixed_command = fix_command(command, args.prompt).strip()

    if (validate_command(fixed_command)):
        # Run the FFmpeg command using subprocess
        print(colored("Running command: " + fixed_command,"green"))
        subprocess.run(fixed_command, shell=True)
    else:
        # Command has potentially extreneous or malicious arguments that shouldn't be run
        print(colored("Potentially harmful command generated. Aborting.","red"))
        print(colored("Failed command: "+command,"red"))

if __name__ == "__main__":
    client = OpenAI(api_key=load_config()["api_key"])
    main()
