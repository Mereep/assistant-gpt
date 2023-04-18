from __future__ import annotations

import logging

import typing

from halo import Halo

from datatypes.chat_context import ChatContext
from gpt_commands import GPT_COMMANDS, ICommand, AskHumanCommand
from utils.human_interaction import ask_human

import gettext

_ = gettext.gettext


def handle_command(
    ctx: ChatContext, command: str, arguments: dict, logger: logging.Logger
) -> str:
    if command not in ctx.settings.allowed_commands:
        logger.warning(f"AI tried to execute disallowed command `{command}`.")
        return "Invalid command."

    command_cls = get_command_cls(command)
    if command_cls.needs_confirmation():
        res = ask_human(
            _("Do you want to execute this command?"),
            prompt_cli=_("Do you want to execute this command? (y/n) [y]"),
            show_options=False,
            options=[_("yes"), _("no")],
            options_cli=[_("yes"), _("no"), _("y"), _("n")],
            default_option=_("yes"),
            repeat_until_valid=True,
            app_settings=ctx.settings,
        )
        if res.lower() in [_("no"), _("n")]:
            return _("Command execution forbidden by user.")

    if not command_cls:
        logger.warning(f"AI tried to execute unknown command `{command}`.")
        return "Invalid command."

    spinner = None
    try:
        if ctx.settings.user_input_prompt_method == 'cli' and command_cls.name() not in [AskHumanCommand.name()]:
            spinner = Halo(text=_("Executing command {}").format(command_cls.name()), spinner="dots")
            spinner.start()

        return command_cls(chat_context=ctx, **arguments)()
    except Exception as e:
        logger.exception(f"Error while executing command `{command}`.")
        return "Error while executing command: " + str(e)
    finally:
        if spinner:
            spinner.stop()


def get_command_cls(command: str) -> typing.Type[ICommand] | None:
    if command not in GPT_COMMANDS.keys():
        return None

    return GPT_COMMANDS[command]
