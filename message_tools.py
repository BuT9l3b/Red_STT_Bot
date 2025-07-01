from typing import Union, List, Optional, Any, Callable
from aiogram.types import Message
import aiogram.exceptions as exc
import telegramify_markdown
import logging
import logfire

import texts

logger = logging.getLogger(__name__)
MAX_MESSAGE_SIZE = 4096


def return_or_false(func):
    """
    Decorator that calls a function and returns its result, True (if the result is None), or False in case of an exception.
    """
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return True if result is None else result
        except Exception as e:
            return False
    return wrapper


class MessageTools:
    """Class with functions simplifying bot interaction"""
    
    @staticmethod
    async def _handle_telegram_error(
        message: Message,
        error: Exception,
        error_type: str,
        fallback_func: Optional[Callable] = None
    ) -> bool:
        """
        Common error handler for Telegram operations. Handles various Telegram API errors
        and provides fallback mechanisms for message sending operations.

        Args:
            message (Message): Telegram message object that caused the error
            error (Exception): The exception that was raised
            error_type (str): Type of operation that failed (e.g., 'message', 'photo', 'voice', 'document')
            fallback_func (Optional[Callable]): Function to retry the operation without reply if needed

        Returns:
            bool: False to indicate operation failure

        Error handling flow:
        1. If error is TelegramBadRequest and message to reply not found:
           - Log warning
           - Retry operation without reply if fallback_func provided
        2. For other TelegramBadRequest errors:
           - Log error
           - Send error message to user
        3. For other exceptions:
           - Log error
           - Send error message to user

        Usage example:
            try:
                await message.reply_photo(photo)
            except Exception as e:
                return await _handle_telegram_error(
                    message, e, "photo",
                    lambda m, is_reply: m.answer_photo(photo)
                )
        """
        user_id = message.from_user.id
        if isinstance(error, exc.TelegramBadRequest):
            if "message to be replied not found" in str(error):
                # Log warning about reply not found and attempt fallback if available
                logfire.warning(f"Error {error_type} for user {user_id} (message to be replied not found)", error=str(error))
                if fallback_func: return await fallback_func(message, is_reply=False)
            else:
                # Log other Telegram API errors and notify user
                logfire.error(f"Error {error_type} for user {user_id}", error=str(error), _exc_info=True)
                await MessageTools.send_response(message, getattr(texts, f"send_{error_type}_error").format(error))
        else:
            # Log unexpected errors and notify user
            logfire.error(f"Error {error_type} for user {user_id}", error=str(error), _exc_info=True)
            await MessageTools.send_response(message, getattr(texts, f"send_{error_type}_error").format(error))
        return False

    @staticmethod
    async def delete_message(message: Message, message_id: int = None):
        """Deletes a message."""
        user_id = message.from_user.id
        try:
            if not message_id: message_id = message.message_id
            await message.chat.delete_message(message_id=message_id)
        except exc.TelegramAPIError as e:
            logfire.error(f"Error deleting message for user {user_id}", error=str(e), _exc_info=True)

    @staticmethod
    async def send_response(message: Message, response: str, is_reply=True, **kwargs) -> Union[List[Message], bool]:
        """Sends a response to the user."""
        user_id = message.from_user.id
        messages = []
        try:
            answ = MessagesEdit.chunks(response, MAX_MESSAGE_SIZE)
            for i, mes in enumerate(answ):
                mes = MessagesEdit.markdown_v2_converter(mes)
                if i == 0 and is_reply:
                    j = await message.reply(mes, **kwargs)
                else:
                    j = await message.answer(mes, **kwargs)
                messages.append(j)
            logfire.info(f"Successfully sent message for user {user_id}")
            return messages
        except exc.TelegramBadRequest as e:
            if "can't parse entities" in str(e):
                logfire.warning(f"Error sending message for user {user_id} (does not match the format)", error=str(e))
                logfire.debug(f"Sent text for user {user_id}", text=response)
                return await MessageTools.send_response(message, response, is_reply, parse_mode=None)
            return await MessageTools._handle_telegram_error(
                message, e, "message",
                lambda m, is_reply: MessageTools.send_response(m, response, is_reply, **kwargs)
            )
        except Exception as e:
            return await MessageTools._handle_telegram_error(message, e, "message")


class MessagesEdit:
    """Class for working with sending text."""

    @staticmethod
    def chunks(s: str, n: int):
        """Splits a string into parts of `n` characters."""
        for start in range(0, len(s), n):
            yield s[start:start + n]

    @staticmethod
    def markdown_v2_converter(text: str) -> str:
        converted = telegramify_markdown.markdownify(
            text,
            max_line_length=None,
            # If you want to change the max line length for links, images, set it to the desired value.
            normalize_whitespace=True,  # Fixes multiple spaces?
            # latex_escape=False  # If you want a normal answer in Latex
        )
        return converted

