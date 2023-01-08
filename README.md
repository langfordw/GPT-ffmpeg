# GPT-FFMPEG Command Line Tool

This is a command line interface tool that uses the OpenAI Completion API to write FFmpeg commands and then run them.

I created this tool for myself to solve a problem that I have: I find it impossible to remember the intricate details of ffmpeg commands. Sure I can do basic file conversions, but anything more complicated than specifying and input file and an output format usually results in 10 minutes of poking around to figure out the right command to do what I want.

This tool solves that problem by letting the user write what they want to do in plain english and converts it to the right ffmpeg command automatically.

**Use this at your own risk. Using this code, you're letting completions generated from OpenAI run directly in your terminal. I've made some minimal effort to protect against malicious code but understand that running this code still poses risk.**

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
# single file
python gpt-ffmpeg.py prompt input_file

# multiple files
python gpt-ffmpeg.py prompt input_file1 input_file2
```

Replace prompt with the prompt to use for generating the FFmpeg command, and replace input_file with the path to the input file.

## Examples
A few examples of how this can be used:

```
python gpt-ffmpeg.py "crop to upper left quadrant" input.png

python gpt-ffmpeg.py "export a separate image crop of each quadrant" input.png

python gpt-ffmpeg.py "convert to png and increase contrast by 25%" input.jpg

python gpt-ffmpeg.py "resize to 640x480" input.mp4

python gpt-ffmpeg.py "convert to an animated gif" input.mp4

python gpt-ffmpeg.py "flip horizontally and convert to mp4" input.mov

python gpt-ffmpeg.py "merge two videos to play back to back" input1.mov input2.mov

python gpt-ffmpeg.py "extract a png frame every 0.5 seconds" input.mp4

python gpt-ffmpeg.py "Create a video from a series of png images at 15fps with a cross compatible codec" input%d.png
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
[OpenAI](https://openai.com/) for providing the Completion API. [FFmpeg](https://ffmpeg.org/) for providing the powerful multimedia framework.