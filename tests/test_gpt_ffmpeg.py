import sys
import types
import importlib.util
from unittest.mock import MagicMock
import pytest

# provide a dummy termcolor so the module can be imported without dependencies
termcolor_mock = types.ModuleType("termcolor")
termcolor_mock.colored = lambda text, *a, **k: text
sys.modules['termcolor'] = termcolor_mock

# create dummy openai module implementing the OpenAI client and
# chat.completions.create that returns different commands depending
# on the prompt so we can test prompt\u2192command pairs
def chat_create_side_effect(model, messages, max_tokens, temperature):
    content = messages[0]["content"]
    if "resize" in content:
        msg = "-vf scale=640:480 output.mp4"
    elif "convert to mp3" in content:
        msg = "-vn -ar 44100 -ac 2 -b:a 192k output.mp3"
    elif "extract frames" in content:
        msg = "-vf fps=5 output_%03d.png"
    else:
        msg = "-c:v libx264 output.mp4"
    return types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=msg))]
    )

completions_mock = MagicMock()
completions_mock.create = MagicMock(side_effect=chat_create_side_effect)

class DummyOpenAI:
    def __init__(self, *a, **k):
        self.chat = types.SimpleNamespace(completions=completions_mock)

openai_mock = types.ModuleType("openai")
openai_mock.OpenAI = DummyOpenAI
sys.modules["openai"] = openai_mock

# load the target module after injecting openai
spec = importlib.util.spec_from_file_location("gpt_ffmpeg", "gpt-ffmpeg.py")
gpt_ffmpeg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpt_ffmpeg)
gpt_ffmpeg.client = DummyOpenAI()


def test_generate_completion_calls_chat_api():
    result = gpt_ffmpeg.generate_completion("resize", "input.mp4")
    assert "output" in result
    completions_mock.create.assert_called_once()
    assert completions_mock.create.call_args[1]["model"] == "gpt-3.5-turbo"


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("resize", "-vf scale=640:480 output.mp4"),
        ("convert to mp3", "-vn -ar 44100 -ac 2 -b:a 192k output.mp3"),
        ("extract frames", "-vf fps=5 output_%03d.png"),
    ],
)
def test_generate_completion_various_prompts(prompt, expected):
    completions_mock.create.reset_mock()
    result = gpt_ffmpeg.generate_completion(prompt, "input.mp4")
    assert result == expected
    completions_mock.create.assert_called_once()
    called_msg = completions_mock.create.call_args[1]["messages"][0]["content"]
    assert prompt in called_msg


def test_fix_command_calls_chat_api():
    completions_mock.create.reset_mock()
    result = gpt_ffmpeg.fix_command("ffmpeg -i input.mp4", "resize")
    assert isinstance(result, str)
    assert result.startswith("ffmpeg")
    completions_mock.create.assert_called_once()
    assert completions_mock.create.call_args[1]["model"] == "gpt-3.5-turbo"


def test_validate_command():
    assert not gpt_ffmpeg.validate_command("rm -rf /")
    assert gpt_ffmpeg.validate_command("ffmpeg -i in.mp4 out.mp4")
