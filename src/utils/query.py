import datetime
import json
import logging

import tiktoken

from datatypes.chat_context import ChatContext
from datatypes.user_message import UserMessage
from gpt_commands import GPT_COMMANDS

query_template = """\
The date and time when sending this message is: {curr_date}.
You are a helpful and smart AI assistant and your name is `{ai_name}`.
You are in a room with the following human(s) {human_names!s}.
You will be supplied with a part of the recent conversation history (as working memory) and the current prompt (next message if any).
As you don't have too much working memory you are encouraged to save important information in your long term memory using the commands given to you. You can only execute one command at a time, so you will have to plan your next steps 
carefully and remember them. If you can, try to answer questions on your own. Please avoid executing the same command twice in a row.

Your general task is to help the human(s). 

You can execute the following commands as desired:
----BEGIN COMMANDS----
{commands}
----BEGIN COMMANDS----
The result of invoking a functionality will be given back to you.

Also, you have access to the following storage keys: {memory_keys} 

We have the following conversation history (with #{n_history} entries total). 
You should incorporate the following information for your answer if useful:
----BEGIN Conversation History----
{history}
----END Conversation History----

!!!Your current prompt / answer is:!!!
{current_prompt}
Additional Information provided: 
{additional_info}
!!!! End current prompt / answer !!!!

---- Your Instructions ----
Plan your next steps carefully step by step and execute them one by one. Remember to add the remaining 
steps to your response in the response template given below. 
Make sure you write the remaining steps you want to do to achieve the plan you make in the 
below given template data structure. 

ALWAYS respond with a JSON object in the following exact format (given as template):
{base_command}

Do *NOT* ander any circumstance respond with a plain string! 
Always use properly formatted unescaped JSON as described above.
"""


def conversation_history_to_str(history: list[tuple[int, str, str]]) -> str:
    return '\n'.join([f'----BEGIN History Entry #{i}----\n{user}: {msg}\n----END History Entry #{i}----' for i, user, msg in history])


def generate_gpt_query(ctx: ChatContext, logger: logging.Logger) -> str:
    """
    Generates a query / prompt for GPT-3
    :param ctx:
    :param logger:
    :return:
    """
    storage = [*ctx.key_storage_backend.list()]
    pos = len(ctx.message_history)
    conversations = []
    if len(ctx.message_history) > 1:
        for i in reversed(ctx.message_history[:-1]):
            conversations.append((pos,
                                  i.user if isinstance(i, UserMessage) else 'assistant',
                                  i.user_response if isinstance(i, UserMessage) else json.dumps(i.dict())
                                  ))
            conversations_str = conversation_history_to_str(conversations)
            n_tokens = count_tokens(text=conversations_str,
                                    model=ctx.settings.model,
                                    logger=logger)
            if n_tokens > ctx.settings.max_token_len_history:
                conversations = conversations[:-1]
                break
            pos -= 1

    # reverse again to be in chronological order
    conversations = [*reversed(conversations)]

    conversations_str = conversation_history_to_str(conversations)

    command_str = ''
    for command_name, command in GPT_COMMANDS.items():
        if command_name in ctx.settings.allowed_commands:
            command_str += f'- `{command_name}` - ({command.description()})\n'
            if command.arguments():
                command_str += 'Args:\n'
                for name, typ, help_text, required in command.arguments():
                    command_str += f'  {name} ({typ.__name__}) - {help_text}' \
                                   f' ({"required" if required else "optional"}\n'
            else:
                command_str += 'No args.\n'

    # current context if available (when it is not the first message)
    if len(ctx.message_history) > 0 and ctx.message_history[-1]:
        additional_info = ctx.message_history[-1].additional_info if ctx.message_history[-1].additional_info else 'None'
        current_prompt = f'User ({ctx.active_user}): ' + ctx.message_history[-1].user_response

    else:
        additional_info = 'None'
        current_prompt = 'None'

    template = query_template.format(
        ai_name=ctx.bot_name,
        human_names=ctx.users,
        memory_keys=storage if storage else 'None',
        n_history=len(ctx.message_history),
        history=conversations_str,
        commands=command_str,
        curr_date=datetime.datetime.now().strftime("%d/%m/%Y at %H:%M:%S"),
        base_command='{"command": "the_command", "arguments": {"the":"parameters", ... }, '
                     '"plan": "the effect you want to achieve with your current execution steps", '
                     '"steps": ["details", "of", "steps", "you", "want", "to", "do"]}',
        #example_command=json.dumps({'command': 'ask_human',
        #                            'arguments': {'information': 'Hello human! How can I help you?'},
        #                            'plan': 'I want to know what to the human needs.',
        #                            'critic': 'Maybe they don\'t need anything.'}),
        current_prompt=current_prompt,
        additional_info=additional_info,
    )

    return template


def count_tokens(text: str, model: str, logger: logging.Logger) -> int:
    """ Count the (approximated) number of tokens of a text for a specific model.
    if the models tokenizer is not available, it will estimate the number of tokens
     by dividing the length of the text by 4 (estimation)
     Parameters:
        text: the text to count the tokens for
        model: the model to count the tokens for
        logger: the logger to log warnings to
    Returns:
        the (maybe estimated) number of tokens
    """
    # To get the tokenizer corresponding to a specific model in the OpenAI API:
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception as e:
        logger.warning(f'Could not get tokenizer for model `{model}`: `{e}`. Will estimate tokens.')
        return len(text) // 4 + 1
