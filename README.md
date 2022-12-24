# GPT-FFMPEG Command Line Tool

This is a command line interface tool that uses the OpenAI Completion API to write FFmpeg commands and then run them.

## Installation
To install the required packages, run the following command:

```
pip install -r requirements.txt
```

## Configuration
Create a config.json file in the same directory as the Python script and store your OpenAI API key in the file like this:

```
{
    "api_key": "YOUR_SECRET_KEY"
}
```

Make sure to replace YOUR_SECRET_KEY with your actual secret key.

## Usage
To run the script, use the following command:

```
python gpt-ffmpeg.py prompt input_file
```

Replace prompt with the prompt to use for generating the FFmpeg command, and replace input_file with the path to the input file.

## Example
To resize an input file to 640x480 and save the output to output.mp4, use the following command:

```
python gpt-ffmpe.py "resize to 640x480" input.mp4
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
[OpenAI](https://openai.com/) for providing the Completion API.
[FFmpeg](https://ffmpeg.org/) for providing the powerful multimedia framework.