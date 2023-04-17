from __future__ import annotations

import json
import logging

import openai
import requests

from datatypes.chat_context import ChatContext
from datatypes.gpt_response import GptResponse
from exceptions.chat_gpt import ChatGptNotInitialized, ChatGptNetworkError, ChatGptHttpResponseFailure, \
    ChatGptApiResponseFormatError, ChatGptResponseFormatError
import gettext

from gpt_commands import AnswerCommand

_ = gettext.gettext

open_ai_is_init = False


def send_message(user_message: str, model: str, logger: logging.Logger, custom_system_role: str | None = None) -> str:
    """
    Sends a message to the chatgpt api and returns the response.

    Args:
        user_message: The message to send to the chatgpt api.
        model: The model to use for the chatgpt api.
        logger: The logger to use for logging.
        custom_system_role: The custom system role to use for the chatgpt api.
        if not given ChatGPT will be tuned being an Assistant.
    Returns:
        The response from the chatgpt api.
    Raises:
        ChatGptNotInitialized: If the chatgpt api was not initialized.
        ChatGptNetworkError: If there was an error while sending the message to the chatgpt api.
        ChatGptHttpResponseFailure: If the chatgpt api responded with a status code != 200.
        ChatGptFormatError: If the chatgpt api responded with an invalid format.
    """
    if not open_ai_is_init:
        raise ChatGptNotInitialized()

    try:
        msg = requests.post('https://api.openai.com/v1/chat/completions',
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {openai.api_key}'
                            },
                            data=json.dumps({
                                'model': model,
                                'messages': [
                                    {'role': 'system',
                                     'content': custom_system_role or 'Assistant is helpful, friendly and knowledgeable agent. '
                                                                      'The assistant always answers exactly in the format specified.'
                                                                      'The Assistant does not respond twice with the same answer.'},
                                    {'role': 'user', 'content': user_message},
                                ],
                                'temperature': 0.1,
                            }))
    except Exception as e:
        logger.error(f"Error while sending message to chatgpt due to `{e}`")
        raise ChatGptNetworkError(e)

    if msg.status_code != 200:
        logger.error(f"Error while sending message to chatgpt. Status code: {msg.status_code}. Content: {msg.content}")
        raise ChatGptHttpResponseFailure(
            "Error while sending message to chatgpt. Status code: {msg.status_code}. Content: {msg.content}")

    msg = msg.json()
    if 'choices' not in msg:
        logger.error(f"Error while sending message to chatgpt. No choices in response. "
                     f"Status code: {msg.status_code}. Content: {msg.content}")
        raise ChatGptApiResponseFormatError(f"Error while sending message to chatgpt. No choices in response. "
                                            f"Status code: {msg.status_code}. Content: {msg.content}")
    msg = msg['choices'][0]['message']['content']

    return msg


def try_parse_response(response: str,
                       ctx: ChatContext,
                       logger: logging.Logger,
                       n_attempts: int = 0) -> GptResponse:
    """ Tries to parse the response from the chatgpt api.
    this function calls itself recursively if the response is not in the correct format.
    until the configured number of attempts is reached.
    Args:
        response: The response from the chatgpt api.
        ctx: The chat context.
        logger: The logger to use for logging.
        n_attempts: The number of attempts to parse the response.
    Returns:
        The parsed response as object of possible or a Dummy response with `gpt_response_error`
        if the response could not be parsed as json
    """
    try:
        response_json = json.loads(response.strip())
        if isinstance(response, list):
            logger.warning(f"Response from chatgpt is a list. It may want to execute multiple commands."
                           f" Returning only the first element.")
            response = response[0]

        resp = GptResponse(
            command=response_json['command'],
            arguments=response_json['arguments'] if 'arguments' in response_json else response[
                'args'] if 'args' in response_json else {},
            plan=response_json['plan'] if 'plan' in response_json else None,
            steps=response_json['steps'] if 'steps' in response_json else [],
        )
        return resp
    except Exception as e:
        logger.error(f"Error while parsing response from chatgpt due to `{e}`. Trying to repair response.")
        try:
            response_str, success = try_repair_response(response, ctx,
                                                        logger)  # this is in the correct format if returned
            if success:
                logger.info(f"Successfully repaired response from chatgpt to correct format.")
                response = json.loads(response_str.strip())
                if isinstance(response, list):
                    logger.warning(f"Response from chatgpt is a list. It may want to execute multiple commands."
                                   f" Returning only the first element.")
                    response = response[0]
                return GptResponse(
                    command=response['command'],
                    arguments=response['arguments'] if 'arguments' in response else response[
                        'args'] if 'args' in response else {},
                    plan=response['plan'] if 'plan' in response else None,
                    # critic=response['critic'] if 'critic' in response else None,
                )
            else:
                # maybe retry
                n_attempts += 1
                if n_attempts < ctx.settings.max_response_repairment_attempts:
                    logger.info(f"Retrying to parse response from chatgpt. Attempt #{n_attempts}.")
                    return try_parse_response(response=response_str,
                                              ctx=ctx, logger=logger, n_attempts=n_attempts)

        except Exception as e:
            logger.error(f"Error while repairing response from chatgpt due to `{e}`. "
                         f"Returning error response.")
            logger.exception(e)
            return GptResponse(command='gpt_response_error',
                               plan="try to recover the conversation",
                               steps=["Fix message", "Continue conversation where we left off"],
                               arguments={
                                   'message': _('You returned an invalid response: `{response}`, '
                                                'which I could not fix!'
                                                '*Always* respond in the described format!').format(response=response)})


def try_repair_response(response: str, ctx: ChatContext, logger: logging.Logger) -> tuple[str, bool]:
    """
    Tries to repair the response from the bot
    will try iterations of trivial methods and then try to repair via model

    :param response: last response from the bot
    :param ctx:
    :param logger:
    :return: (repaired response or current state of repairment, bool if the message is a valid json)
    :raises: ChatGptResponseFormatError if the response could not be repaired and retries are likely not going to help
    """
    response = response.strip()
    if not '{' or '}' not in response:
        # if there are no brackets, the model likely did just want to answer a question
        # and didn't get to return a command. So we interpret the response as an answer
        logger.info(f"Response from chatgpt did not contain a command at all. "
                    f"Will interpret it as an straight answer.")
        return json.dumps(GptResponse(command=AnswerCommand.name(),
                                      plan="Recover the plan",
                                      steps=["Repair the current prompt", "Continue conversation where we left off"],
                                      # critic='This message was no valid json. Only use json as response.',
                                      arguments={'answer': response}).dict()), True

    first_bracket = response.index('{')
    last_bracket = response.rindex('}')
    within_brackets = response[first_bracket:last_bracket + 1]
    before_brackets = response[:first_bracket].strip()
    # check if something is after the last bracket
    if last_bracket + 1 < len(response):
        after_brackets = response[last_bracket + 1:].strip()
    else:
        after_brackets = ''

    dangling_text = before_brackets + '.' + after_brackets

    try:
        # if this works, we are likely done
        j = json.loads(within_brackets)
        if isinstance(j, list):
            logger.warning(f"Response from chatgpt is a list. It may want to execute multiple commands."
                           f" Returning only the first element.")
            j = j[0]
        # or not so much, though
        if 'command' in j:
            if not j['command']:
                logger.warning(f"Response from chatgpt contained an empty command. ")
                if len(dangling_text) > 1:
                    logger.info(f"There seems to be some dangling text. I will try using it to fix the situation.")
                    j['command'] = before_brackets
                    return str(GptResponse(command=AnswerCommand.name(),
                                           plan="Recover the plan",
                                           steps=["Repair the current prompt",
                                                  "Continue conversation where we left off"],
                                           arguments={'answer': response}).dict()), True
                else:
                    logger.warning(f"Couldn't fix the empty command as there was no dangling text outside the command.")
                    raise Exception("Empty command")
            else:  # happy case we have a non-empty command
                return within_brackets, True
        if dangling_text:  # no `command` key but there is some dangling text
            return json.dumps(GptResponse(command=AnswerCommand.name(),
                                          plan="Recover the plan",
                                          steps=["Repair the current prompt",
                                                 "Continue conversation where we left off"],
                                          arguments={'answer': response}).dict()), True
    except:
        pass  # keep going

    # fix for double escaped quotes (this may be wrong as json in json might be broken using this)
    if '\\"' in within_brackets:
        within_brackets = within_brackets.replace('\\"', '{"')
        try:
            json.loads(within_brackets)
            return within_brackets, True
        except:
            pass

    logger.warning(f"Could not repair response via trivial methods. Trying to repair via model.")
    try:
        result = try_repair_json_using_bot(response=response, ctx=ctx, logger=logger)
        try:
            j = json.loads(result)
            if isinstance(j, list):
                logger.warning(f"Response from chatgpt is a list. It may want to execute multiple commands."
                               f" Returning only the first element.")
                j = j[0]
            return json.dumps(j), True
        except:
            logger.warning(f"Could not repair response via model, but got a successful response."
                           f"Maybe another attempt will work.")
            return result, False

    except Exception as e:
        logger.error(f"Error while trying to repair response via model due to `{e}`")
        raise ChatGptResponseFormatError(f"Error while trying to repair response via model due to `{e}`") from e


def try_repair_json_using_bot(response: str, ctx: ChatContext, logger: logging.Logger) -> str:
    """ Tries to repair the response from the chatgpt api via the bot.
    :param response: The response from the chatgpt api.
    :param ctx: The chat context.
    :param logger: The logger to use for logging.
    :raises Exception: if there is an error communicating with the repairment bot
    :return: The repaired response.
    """
    query = """
    The following snippet is a broken json:
    {broken_json}

    Please repair it to valid json that could be loaded for example by Pythons json.loads function.
    Importantly: do **only** answer with a valid json structure. No other messages and no textual explanations allowed!
    """
    query = query.format(broken_json=response)
    return send_message(user_message=query, model=ctx.settings.model, logger=logger)


def list_models() -> dict[dict]:
    if not open_ai_is_init:
        raise ChatGptNotInitialized()

    return openai.Engine.list()


def initialize(api_key: str, org: str | None = None):
    global open_ai_is_init
    if not open_ai_is_init:
        openai.api_key = api_key
        if org:
            openai.organization = org
        open_ai_is_init = True
