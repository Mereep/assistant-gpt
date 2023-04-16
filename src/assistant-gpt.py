from __future__ import annotations

import logging
from pathlib import Path
from time import sleep

from halo import Halo
from rich.style import Style

from datatypes.chat_context import ChatContext
from datatypes.cli_format import CliFormat
from datatypes.gpt_response import GptResponse
from datatypes.user_message import UserMessage
from exceptions.commands_execption import ArgumentMissingException, ArgumentTypeException, CommandExecutionError
from exceptions.settings_exception import SettingsException
from gpt_commands import AnswerCommand
from logger.base_logger import get_base_logger
from utils import chatgpt
from utils.app_settings import AppSettings
from utils.chatgpt import try_parse_response
from utils.command import handle_command
from utils.human_interaction import tell_human, ask_human, present_bot_response_command, typewriter_effect
from utils.conversations import available_conversations, load_conversation, save_conversation

import gettext

from utils.query import generate_gpt_query, count_tokens
from utils.storage import load_key_storage_backend, load_file_storage_backend

_ = gettext.gettext


def initiate_conversation(app_settings: AppSettings, logger: logging.Logger) -> ChatContext:
    chatgpt.initialize(api_key=app_settings.gpt_api_key)
    available_models = chatgpt.list_models()['data']
    if app_settings.model not in [model['id'] for model in available_models]:
        raise SettingsException(f"Model {app_settings.model} is not available. ")

    available_conversation_ids = available_conversations(app_settings=app_settings)

    tell_human(_("Welcome to your personal assistant!\n"), app_settings=app_settings)
    conversation: ChatContext | None = None
    typewrite_style = CliFormat(
        delay=0.03,
    )
    if available_conversation_ids:
        tell_human(_("You have the following conversations started:"), app_settings=app_settings)
        for conv in available_conversation_ids:
            tell_human(f"- {conv}", app_settings=app_settings)
        load = _("no")
        try:
            repeat = True
            while repeat:
                load = ask_human(_("Do you want to continue an existing conversation?"),
                                 options=[_("yes"),
                                          _("no")],
                                 app_settings=app_settings
                                 )
                load = load.lower()
                if load in [_("yes"), _("no")]:
                    repeat = False

        except Exception as e:
            tell_human(_("Operation cancelled. Continuing with creating a new conversation."),
                       app_settings=app_settings)
            logger.error(f"Error while asking user if he wants to load a conversation due to {e}."
                         f"Assuming user wants to start a new conversation.")
            load = _("no")

        if load == _("yes"):
            repeat = True
            conversation_id = None
            while repeat:
                try:
                    conversation_id = ask_human(_("Which conversation do you want to continue? "),
                                                options=available_conversation_ids,
                                                app_settings=app_settings
                                                )

                    if conversation_id not in available_conversation_ids:
                        tell_human(_("This conversation {conv} does not exist. "
                                     "Please try again.").format(conv=conversation_id),
                                   app_settings=app_settings)
                        repeat = True
                    else:
                        repeat = False
                except Exception as e:
                    tell_human(_("Operation cancelled. Continuing with creating a new conversation."),
                               app_settings=app_settings)
                    logger.error(f"Error while asking user which conversation to load due to {e}."
                                 f"Assuming user wants to start a new conversation.")
                    repeat = False
                    conversation_id = None

            try:
                if conversation_id:
                    conversation = load_conversation(conversation_id=conversation_id,
                                                     logger=logger,
                                                     app_settings=app_settings)
            except Exception as e:
                logger.error(f"Error while loading conversation {conversation_id} due to {e}.")
                tell_human(_("Error while loading conversation {conv}. Starting a new one.").format(conv=conversation),
                           app_settings=app_settings)
                conversation = None
        else:
            tell_human(_("Great, let's begin something new"), app_settings=app_settings, style=typewrite_style)
            conversation = None

    if not conversation:
        own_name = ask_human(_("What is your name? "),
                             style=typewrite_style,
                             app_settings=app_settings)
        ai_name = 'assistant'

        conversation_id = ask_human(_("How do we want to call this conversation? (to restore it later)"),
                                    style=typewrite_style,
                                    app_settings=app_settings)

        conversation = ChatContext(users=[own_name],
                                   active_user=own_name,
                                   bot_name=ai_name,
                                   settings=app_settings,
                                   conversation_id=conversation_id,
                                   key_storage_backend=load_key_storage_backend(app_settings=app_settings,
                                                                                conversation_id=conversation_id),
                                   file_storage_backend=load_file_storage_backend(app_settings=app_settings,
                                                                                  conversation_id=conversation_id),
                                   default_logger=logger,
                                   )
        save_conversation(ctx=conversation)

    return conversation


def main():
    logger = get_base_logger()
    settings = AppSettings(config_file=Path('..') / 'settings.yaml')
    logger.setLevel(settings.log_level.upper())
    conversation = initiate_conversation(app_settings=settings, logger=logger)

    run_loop(conversation=conversation, logger=logger)


def run_loop(conversation: ChatContext, logger: logging.Logger):
    typewrite_style = CliFormat(
        delay=0.03,
    )

    app_settings = conversation.settings

    tell_human(_("Hello {name}! Conversation {conv} started!").format(
        name='and'.join(conversation.users), conv=conversation.conversation_id),
        app_settings=conversation.settings)

    if conversation.message_history:
        tell_human(
            _("This conversation has already {n_messages} messages").format(
                n_messages=len(conversation.message_history)),
            app_settings=conversation.settings)
    while True:
        if len(conversation.message_history) == 0:
            user_turn = False
            tell_human(_("I will start a new conversation."),
                       app_settings=conversation.settings)
        else:
            user_turn = isinstance(conversation.message_history[-1], GptResponse)

        if not user_turn:
            message_for_bot = generate_gpt_query(ctx=conversation, logger=logger)
            tell_human(_("Transmitting query with {n_tokens} tokens".format(
                n_tokens=count_tokens(message_for_bot,
                                      model=conversation.settings.model,
                                      logger=logger)
                )),
                app_settings=app_settings
            )
            tell_human(_("Talking to AI..."), app_settings=conversation.settings)
            spinner = Halo(text=_("Thinking..."), spinner='dots')
            spinner.start()
            response: str | None = None
            try:
                response = chatgpt.send_message(user_message=message_for_bot,
                                                logger=logger,
                                                model=conversation.settings.model)
                spinner.stop()

                tell_human(_("Received a response with {n_tokens} tokens".format(
                    n_tokens=count_tokens(response,
                                          model=conversation.settings.model,
                                          logger=logger)
                )),
                    app_settings=app_settings,
                    style=typewrite_style
                )

            except Exception as e:
                tell_human(_("Error while talking to AI. Please try again."),
                           app_settings=conversation.settings)
                logger.error(f"Error while talking to AI due to {e}.")
            finally:
                spinner.stop()

            if not response:
                res = ask_human(_("Try again?"),
                                options=[_("yes"), _("no")],
                                repeat_until_valid=True,
                                app_settings=conversation.settings)
                if res.lower() == _("yes"):
                    continue

                if res.lower() == _("no"):
                    exit(0)
            else:
                parsed = try_parse_response(response=response, ctx=conversation, logger=logger)
                conversation.message_history.append(parsed)
                logger.debug(f"Saving conversation {conversation.conversation_id}")
                save_conversation(ctx=conversation)
        else:  # User turn
            bot_response = conversation.message_history[-1]
            present_bot_response_command(bot_response=bot_response,
                                         ctx=conversation,
                                         logger=logger)
            if bot_response.command == 'gpt_response_error':
                tell_human(_("Error while talking to AI. "
                             "You might want to remind it to response in proper format or ask it to repair the last "
                             "response. Please try again."),
                           app_settings=conversation.settings)
                message = ask_human(_("Feedback to AI: "),
                                    app_settings=conversation.settings)
                additional_info = None
            else:
                additional_info = None
                try:
                    response = handle_command(command=bot_response.command,
                                              arguments=bot_response.arguments,
                                              logger=logger,
                                              ctx=conversation)

                except ArgumentMissingException as e:
                    response = f'Argument: {e.argument} is missing for command {parsed.command}.'
                except ArgumentTypeException as e:
                    response = f'Argument: {e.argument} has wrong type for command ' \
                               f'(expected: {e.expected_type}) found {e.found_type} for {parsed.command}.'
                except CommandExecutionError as e:
                    response = f'Error while executing command {parsed.command} due to {e.reason_for_bot}'
                except Exception as e:
                    response = f'Unknown Error while executing command {parsed.command} due to {e}'
                tell_human(_("Command response: {}.").format(response),
                           app_settings=app_settings)

                # Do not feed back the answer to the bot
                if bot_response.command == AnswerCommand.name():
                    message = ask_human(_("You received an answer. Add a response for {}: ").format(conversation.bot_name),
                                        app_settings=app_settings)

                else:
                    # collect some additional info
                    if app_settings.user_input_prompt_method == 'cli':
                        typewriter_effect(text='\n-> ', new_line=False, style=Style(color='green'))
                    additional_info = ask_human(_("Ready to send response. "
                                                  "Add an additional message for {} (if you like, leave blank if no info): ").format(conversation.bot_name),
                                                app_settings=app_settings)

                    # just convenient for people used to enter `no` instead of leaving it blank
                    if additional_info == _("no"):
                        additional_info = None

                    # write the command response as message
                    message = response

            conversation.message_history.append(UserMessage(user_response=message,
                                                            additional_info=additional_info,
                                                            user=conversation.active_user))
            logger.debug("Saving conversation...")
            save_conversation(ctx=conversation)


sleep(2)  # just to not flood messages

if __name__ == "__main__":
    main()
