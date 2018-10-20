from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
from itertools import count
import random

# from database import add_friend, get_friends_count

from settings import MIN_FRIEND_COUNT

OLOLO = 0


def add_friend(a, b):
    OLOLO += 1


def get_friends_count():
    return OLOLO


class Stage:
    @classmethod
    def get_handlers():
        raise NotImplementedError()


class AddFriends(Stage):
    name = "ADD_FRIENDS"

    @classmethod
    def get_handlers(cls):
        return [MessageHandler(Filters.text, cls.add_friend)]

    @classmethod
    def add_friend(cls, bot, update):
        user_id = update.message.from_user.id
        friend_user_name = update.message.text
        try:
            friend_id = 1  # TODO
        except Exception as e:
            update.message.reply_text
        add_friend(user_id, friend_id)
        if get_friends_count(user_id) >= MIN_FRIEND_COUNT:
            update.message.reply_text(
                'Great! You may enter more friends nicknames,'
                'then it\'s enough press "Done". You also may add more friends later',
                reply_markup=ReplyKeyboardMarkup([['Done']], one_time_keyboard=True)
            )
        return cls.name


class Controller:
    @classmethod
    def run_bot(cls, token):
        cls._updater = Updater(token)
        dispatcher = cls._updater.dispatcher

        meeting_conversation_stages = [AddFriends, ]
        meeting_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', cls.start_meeting)],
            stages={stage.name: stage.get_handlers() for stage in meeting_conversation_stages},
        )

        dispatcher.add_handler(meeting_conversation_handler)
        cls._updater.start_polling()
        cls._updater.idle()

    @staticmethod
    def start_meeting(bot, update):
        update.message.reply_text(
            'Hello! Tell me your friendns\' nicknames in Telegram.'
            'Type at least three and then click "Done"'
        )

        return AddFriends.name
