#!/opt/homebrew/bin/python3
import argparse
import openai
import subprocess
import os
import json

def load_config():
    """
    Load the configuration from a JSON file.
    """
    with open("config.json") as f:
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str, help="prompt to use for generating completion")
    parser.add_argument("input_file", type=str, help="input file path")
    args = parser.parse_args()

    # Generate a completion using the OpenAI Completion API
    completion = generate_completion(args.prompt, args.input_file)
    completion = completion.replace('output.','"'+os.path.abspath('.')+'/output.')
    command = 'ffmpeg -i "'+os.path.abspath(args.input_file)+'" '+completion+'"'
    print(command)
    
    # Run the FFmpeg command using subprocess
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()
