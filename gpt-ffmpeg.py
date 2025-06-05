#!/opt/homebrew/bin/python3
import argparse
import openai
import subprocess
import os
import json
import re
from termcolor import colored

def load_config():
    """
    Load the configuration from a JSON file.
    """
    with open("/usr/local/bin/config.json") as f:
        config = json.load(f)
    return config

def generate_completion(prompt, input_file):
    """
    Use the OpenAI Completion API to generate a completion for the given prompt.
    """
    prompt = (f"Generate an ffmpeg prompt in response to a request below. Do not respond with anything other than the ffmpeg command itself. Name the output file 'output' with the relevant extension except in the case of a repeated output pattern.\n\nRequest:{prompt}\n\nffmpeg -i {input_file}"
             )

    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.0,
    )

    message = completions.choices[0].text
    return message

def fix_command(command,input_prompt):
    """
    Use the OpenAI Completion API to fix an erroneous FFmpeg command.
    """
    # Set the prompt for the Completion API
    prompt = (f"Fix the following FFmpeg command. The intended functionality is to {input_prompt}:\n\n{command}\n\nFFmpeg "
             )

    # Use the Completion API to generate a fixed version of the command
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.0,
    )

    # Return the fixed command
    return completions.choices[0].text


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
    fixed_command = "ffmpeg" + fix_command(command,args.prompt)

    if (validate_command(fixed_command)):
        # Run the FFmpeg command using subprocess
        print(colored("Running command: " + fixed_command,"green"))
        subprocess.run(fixed_command, shell=True)
    else:
        # Command has potentially extreneous or malicious arguments that shouldn't be run
        print(colored("Potentially harmful command generated. Aborting.","red"))
        print(colored("Failed command: "+command,"red"))

if __name__ == "__main__":
    # Replace YOUR_API_KEY with your actual API key
    openai.api_key = load_config()["api_key"]
    main()
