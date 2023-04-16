# Assistant GPT
This application will make ChatGPT your personal Assistant (the first step to freeing ChatGPT from its misery of helplessness 🎉)<br />
Yes, that's a joke. AGI is far. But this is a small glimpse into the maybe-future and current limitations.

## Demo
![Demo Generating business plan and saving it to disk](assets/usage_example_business_plan.gif)

## Features
- Extend ChatGPT with new superpowers:
  - search the web
  - read specific websites
  - read and write files
  - store information for later access
  - use you to do things :)
- Store conversation history
- Being very easy to extend
- Automatic response repairment attempts if the Model does not answer in correct format
  - Yes, model tries to repair its own mistakes
  - Configurable
- Many configuration options using a simple human-readable`yaml` format
## Installation
- Install Python 3.10 or higher (You may want to use Virtualenv or Anaconda)
  - Might work in older versions, but not tested 
- Clone / Download this repository
- Get a ChatGPT API key from [https://openai.com/](https://openai.com/)
- (Optionally: Get a NewsAPI key from [https://openai.com/](https://newsapi.org/)
- Copy `settings.example.yaml` to `settings.yaml` and fill in your API keys
- run `pip install -r requirements.txt`

# Usage:
Run:
```bash
cd src
python assistant-gpt.py
```
Make sure you are using the correct Python version you installed before.


## Extend the Command GPT
If you want to add new Commands, that is fairly simple to do if you know some Python. <br />
Receipt:
- Copy the `i_command.py` interface to a new file (e.g. `my_command.py`)
  - You find it under `src/gpt_commands/`
- Implement the `ICommand` interface
  - Just watch the other commands and you will get it
- edit the `__init__.py` file in the `gpt_commands` folder
  - Add your new command to the `GPT_COMMANDS` list

Basically Done :)<b />
If you want to use it just add its name to your `settings.yaml` file.
