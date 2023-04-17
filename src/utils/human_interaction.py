from __future__ import annotations

import json
from logging import Logger

from rich.style import Style

from datatypes.chat_context import ChatContext
from datatypes.cli_format import CliFormat
from datatypes.gpt_response import GptResponse
from exceptions.user_interaction import InteractionNotPossible
from utils.app_settings import AppSettings
import gettext
from rich.text import Text
from rich.console import Console
import time

console = Console()
_ = gettext.gettext


def typewriter_effect(text,
                      style=None,
                      delay=0.02,
                      new_line=True):
    for char in text or '':
        console.print(Text(char, style=style), end="")
        time.sleep(delay)

    if new_line:
        console.print()


def ask_human(prompt: str,
              app_settings: AppSettings,
              options: list[str] | None = None,
              repeat_until_valid: bool = False,
              option_details: dict[str, str] | None = None,
              style: CliFormat | None = None,
              ) -> str:
    """
    Reads a string from the user.
    Args:
        prompt: the prompt to show the user
        app_settings: the application settings
        options: the options the user can choose from (will not be checked just presented)
        option_details: descriptions for the options (may or may not be presented)
        repeat_until_valid: if True, the user will be asked again if he entered an invalid option
        style: the style to use for the prompt output
    Raises:
        InteractionNotPossible: when the communication method is not available
        CouldNotGetResponse: when the user didn't enter anything
    """
    if app_settings.user_input_prompt_method == 'cli':
        prompt = prompt.strip()
        if options:
            prompt += f" ({', '.join(options)})"

        tell_human(prompt, app_settings=app_settings, style=style)
        user_input = input()
        if options and user_input not in options and repeat_until_valid:
            tell_human(_("Invalid option. Please try again."), app_settings=app_settings, style=style)
            return ask_human(prompt=prompt,
                             app_settings=app_settings,
                             options=options,
                             repeat_until_valid=repeat_until_valid,
                             option_details=option_details,
                             style=style,
                             )
        return user_input.strip()

    else:
        raise InteractionNotPossible(f"User input prompt method `{app_settings.user_input_prompt_method}` "
                                     f"is not implemented.")


def present_bot_response_command(ctx: ChatContext,
                                 bot_response: GptResponse,
                                 logger: Logger):
    app_settings = ctx.settings
    if ctx.settings.user_input_prompt_method == 'cli':
        style_green = Style(color='green', bold=True)
        style_command = Style(color='red', underline=True)
        style_white = Style(color='white')
        typewriter_effect(_("Response from AI: "), style=style_green)
        typewriter_effect(_("Command: "), style=style_green, new_line=False)
        typewriter_effect(bot_response.command, style=style_command)
        typewriter_effect(_("Arguments: "), style=style_green, new_line=False)
        typewriter_effect(json.dumps(bot_response.arguments), style=style_white, delay=0.00)
        typewriter_effect(_("Plan: "), style=style_green, new_line=False)
        typewriter_effect(bot_response.plan, style=style_white)
        typewriter_effect(_("Steps: "), style=style_green, new_line=True)
        typewriter_effect('\n- '.join(bot_response.steps), style=style_white)
        typewriter_effect("------------------", style=style_white, new_line=False)
        typewriter_effect("\n", new_line=False)
    else:
        tell_human("Response from AI: ", app_settings=app_settings)
        tell_human(_("Command: {}").format(), app_settings=app_settings)
        tell_human(_("Arguments: {}").format(bot_response.arguments), app_settings=app_settings)
        tell_human(_("Plan: {}").format(bot_response.plan), app_settings=app_settings)
        tell_human(_("Steps: {}").format(str(bot_response.steps)), app_settings=app_settings)
        #tell_human(_("Critic: {}").format(bot_response.critic), app_settings=app_settings)


def tell_human(message: str,
               app_settings: AppSettings,
               style: CliFormat | None = None
               ) -> None:
    """
    Tells the user something.
    Args:
        message: the message to tell the user
        app_settings: the application settings
        style: the style to optionally when outputting to cli
    Raises:
        InteractionNotPossible: when the communication method is not available
    """
    style = style or CliFormat()
    if app_settings.user_input_prompt_method == 'cli':
        typewriter_effect(message, style=style.style, delay=style.delay, new_line=style.new_line)

    else:
        raise InteractionNotPossible(f"User input prompt method `{app_settings.user_input_prompt_method}` "
                                     f"is not implemented.")
