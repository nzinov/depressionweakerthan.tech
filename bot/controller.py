from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, RegexHandler
)
from itertools import count
import random
import logging

# from database import add_friend, get_friends_count, get_user_id_by_username,
# get_all_subscriptions

from settings import MIN_FRIEND_COUNT

global OLOLO
OLOLO = 0

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def add_friend_to_user(a, b):
    global OLOLO
    OLOLO += 1


def get_user_id_by_username(username):
    return {
        'Leshka': 270200185,
    }.get(username)


def get_friends_count(user_id):
    return OLOLO


class Stage:
    @classmethod
    def get_handlers():
        raise NotImplementedError()


class AddFriends(Stage):
    name = "ADD_FRIENDS"
    _done = 'Done'

    @classmethod
    def get_handlers(cls):
        return [
            RegexHandler('^' + cls._done + '$', cls.done),
            MessageHandler(Filters.text, cls.add_friend),
        ]

    @classmethod
    def add_friend(cls, bot, update):
        user = update.message.from_user

        friend_username = update.message.text
        logger.info('User {} want to add friend {}'.format(user.id, friend_username))
        friend_id = get_user_id_by_username(friend_username)
        if friend_id is None:
            update.message.reply_text(
                "This user didn't communication with me yet. Please share with him a link: "
                "t.me/depression_weaker_than_tech_bot"
            )
        else:
            bot.send_message(
                friend_id,
                'User ' + user.username + ' add you as friend. '
                'If it has depression you will be notified'
            )

        logger.info('Found friend id: ' + str(friend_id))
        add_friend_to_user(user.id, friend_id)
        curr_friends_count = get_friends_count(user.id)

        if curr_friends_count >= MIN_FRIEND_COUNT:
            if curr_friends_count == MIN_FRIEND_COUNT:
                reply_markup = ReplyKeyboardMarkup([[cls._done]], one_time_keyboard=True)
            else:
                reply_markup = None
            update.message.reply_text(
                'Great! You may enter more friends usernames, '
                'then it\'s enough press "' + cls._done + '". You also may add more friends later',
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(
                'Good! Now I know {} your friend(s). '.format(curr_friends_count) +
                'Tell me more friends!'
            )
        return cls.name

    @classmethod
    def done(cls, bot, update):
        update.message.reply_text(
            'Well done! Now if I think you have a depression, I\'ll concact your friends!'
        )


class Controller:
    @classmethod
    def run_bot(cls, token):
        cls._updater = Updater(token)
        dispatcher = cls._updater.dispatcher

        meeting_conversation_stages = [AddFriends, ]
        meeting_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', cls.start_meeting)],
            states={stage.name: stage.get_handlers() for stage in meeting_conversation_stages},
            fallbacks=[],
        )
        dispatcher.add_handler(meeting_conversation_handler)

        cls._updater.start_polling()
        cls._updater.idle()

    @staticmethod
    def start_meeting(bot, update):
        update.message.reply_text(
            'Hello! Tell me your friendns\' usernames in Telegram. '
            'Type at least three and then click "Done"'
        )

        # subscriptions = get_all_subscriptions(update.message.from_user.id)
        # for subscription in subscriptions:

        return AddFriends.name
