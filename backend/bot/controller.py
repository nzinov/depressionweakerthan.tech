from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, RegexHandler,
)
from itertools import count
import random
import logging

# from database import add_subscriber, get_subscribers_count, get_user_id_by_username,
# get_all_subscriptions
# get_all_subscribers
# add_twitter_login
# send_photo

from .settings import MIN_FRIEND_COUNT, TOKEN
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
from api.models import User


EXTENTION_URL = (
    'https://chrome.google.com/webstore/detail/depressionweakerthan/'
    'npkememoejnlkmfojaaobeahlepddgad/related?depressionweakerthan_user_id={}'
)

global OLOLO
OLOLO = 0


def analyze_photo(user_id, photo_path):
    pass


def add_twitter_login(user_id, login):
    pass


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def add_subscriber_to_user(a, b):
    global OLOLO
    OLOLO += 1


def get_all_subscribers(user_id):
    return {
        296688575: [270200185],
        270200185: [296688575],
    }.get(user_id)


def get_all_subscriptions(user_id):
    return [270200185]


def get_user_id_by_username(username):
    return {
        '@Onaga1958': 270200185,
        '@PKoshkin': 225128072,
        '@nzinov': 296688575,
        '@RakcheevEvgeny': 267804759,
    }.get(username)


def get_subscribers_count(user_id):
    return OLOLO


class Stage:
    @classmethod
    def get_handlers(cls):
        raise NotImplementedError()


class AddFriends(Stage):
    name = "ADD_FRIENDS"
    _done = 'Done'

    @classmethod
    def get_handlers(cls):
        return [
            RegexHandler('^' + cls._done + '$', cls.done),
            MessageHandler(Filters.text, cls.add_subscriber),
        ]

    @staticmethod
    def add_friend(friend_username, bot, update):
        user = update.message.from_user
        if friend_username[0] != '@':
            update.message.reply_text('Username should start with @!')
            return False
        else:
            logger.info('User {} want to add friend {}'.format(user.id, friend_username))
            friend_id = get_user_id_by_username(friend_username)
            if friend_id is None:
                update.message.reply_text(
                    "This user didn't communication with me yet. Please share with him a link: "
                    "t.me/depression_weaker_than_tech_bot. Then " + friend_username +
                    " press \"Start\" in chat with me, he or she will be added to your friends."
                )
                logger.info('Not found friend with username: {}'.format(friend_username))
            else:
                add_friend_message = (
                    'User {} add you as friend. '
                    'If one of your friends has depression you will be notified'
                )
                bot.send_message(
                    friend_id,
                    add_friend_message.format(user.name)
                )

                logger.info('Found friend id: ' + str(friend_id))
            add_subscriber_to_user(user.id, friend_id)
            return True

    @classmethod
    def add_subscriber(cls, bot, update):
        friend_username = update.message.text
        if not AddFriends.add_friend(friend_username, bot, update):
            return AddFriends.name

        user_id = update.message.from_user.id
        curr_friends_count = get_subscribers_count(user_id)

        if curr_friends_count >= MIN_FRIEND_COUNT:
            if curr_friends_count == MIN_FRIEND_COUNT:
                reply_markup = ReplyKeyboardMarkup([[cls._done]], one_time_keyboard=True)
            else:
                reply_markup = None
            update.message.reply_text(
                'Great! You may enter more usernames, '
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
            'Well done! Now if I think you have a depression, I\'ll contact your friends!'
        )
        update.message.reply_text(
            'Now, I need some information about you. '
            'Please add my Chrome extention: ' +
            EXTENTION_URL.format(update.message.from_user.id) +
            'I will analyze your websites and calculate statistics'
            ', but I won\'t save your history. Without this extention it won\'t be possible to '
            'know if you have a depression or not.',
            reply_markup=ReplyKeyboardMarkup(
                [[AddExtention.agree_message]], one_time_keyboard=True
            )
        )

        return AddExtention.name


class AddExtention(Stage):
    name = "ADD_EXTENTION"
    agree_message = "I have installed the extention!"

    @classmethod
    def get_handlers(cls):
        return [
            RegexHandler('^' + cls.agree_message + '$', cls.done)
        ]

    @classmethod
    def done(cls, bot, update):
        update.message.reply_text(
            'Great! It will be also helpfull, if you give me your Twitter login. '
            'I will read your posts and posts liked by you. Also, just calculate stats and '
            ' no more. If you don\'t have Twitter or don\'t want to share with me your login '
            ' it\'s okey, just press "' + AddTwitter.skip_message + '".',
            reply_markup=ReplyKeyboardMarkup([[AddTwitter.skip_message]], one_time_keyboard=True)
        )
        return AddTwitter.name


class AddTwitter(Stage):
    name = "ADD_TWITTER"
    skip_message = 'Skip'
    end_message = (
        "Okey! That's all for now. I will send you a notification if someone add you "
        'as friend and if one of your friends has depression. You can type /help '
        'to get help and learn some commands with which '
        'you can call me.'
    )

    @classmethod
    def get_handlers(cls):
        return [
            RegexHandler('^' + cls.skip_message + '$', cls.skip),
            MessageHandler(Filters.text, cls.enter_twitter_login),
        ]

    @classmethod
    def skip(cls, bot, update):
        update.message.reply_text(cls.end_message)
        return ConversationHandler.END

    @classmethod
    def enter_twitter_login(cls, bot, update):
        user = update.message.from_user
        login = update.message.text
        add_twitter_login(user.id, login)
        logger.info('User {} add twitter login {}'.format(user.name, login))
        update.message.reply_text(cls.end_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


class Controller:
    DEPRESSED = "/i_m_depressed"
    ADD_FRIEND = '/add_friend'
    HELP = '/help'

    @classmethod
    def run_bot(cls):
        cls._updater = Updater(TOKEN)
        dispatcher = cls._updater.dispatcher

        meeting_conversation_stages = [AddFriends, AddExtention, AddTwitter, ]
        meeting_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', cls.start_meeting)],
            states={stage.name: stage.get_handlers() for stage in meeting_conversation_stages},
            fallbacks=[],
        )
        dispatcher.add_handler(meeting_conversation_handler)

        dispatcher.add_handler(CommandHandler(
            cls.DEPRESSED[1:],
            lambda bot, update: cls.notify_friends_about_depression(update.message.from_user.id)
        ))
        dispatcher.add_handler(CommandHandler(cls.HELP[1:], cls.print_help))
        dispatcher.add_handler(CommandHandler(cls.ADD_FRIEND[1:], cls.add_friend))

        cls._updater.start_polling()
        cls._updater.idle()

    @classmethod
    def start_meeting(cls, bot, update):
        update.message.reply_text(
            "Hello! "
            'Tell me your friendns\' usernames in Telegram. '
            'Be aware, username should start with @. '
            'Type at least one and then click "Done"'
        )

        subscriptions = get_all_subscriptions(update.message.from_user.id)
        for subscription in subscriptions:
            update.message.reply_text(
                'User {} add you as friend'.format(cls.get_username(subscription))
            )
        update.message.reply_text('If one of your friends has depression you will be notified')

        return AddFriends.name

    @classmethod
    def get_bot(cls):
        if getattr(cls, '_updater', None) is None:
            cls._updater = Updater(TOKEN)
        return cls._updater.bot

    @classmethod
    def get_username(cls, user_id):
        bot = cls.get_bot()
        return bot.get_chat_member(user_id, user_id).user.name

    @classmethod
    def depression_detected(cls, user_id):
        cls.notify_friends_about_depression(cls, user_id)
        cls.notify_user_about_depression(cls, user_id)

    @classmethod
    def notify_user_about_depression(cls, user_id):
        bot = cls.get_bot()

    @classmethod
    def notify_friends_about_depression(cls, user_id):
        bot = cls.get_bot()
        username = cls.get_username(user_id)
        for subscriber in get_all_subscribers(user_id):
            bot.send_message(subscriber, 'Your friend, ' + username + ', is depressed!')

    @classmethod
    def print_help(cls, bot, update):
        update.message.reply_text(
            'Type ' + cls.HELP + ' to get help (prints this message).\n'
            'Type ' + cls.DEPRESSED + ' to tell your freinds that your is depressed.\n'
            'Type "' + cls.ADD_FRIEND + ' @friend_username" to add person with username '
            '@friend_username to your friends. He or she will be notified if I somehow '
            'realize that you is depressed.'
        )

    @classmethod
    def send_photo(cls, bot, update):
        photo_file = bot.get_file(update.message.photo[-1].file_id)
        user = update.message.from_user
        photo_file_name = '{}_photo.jpg'.format(user.name)
        photo_file.dowload(photo_file_name)
        logger.info("Photo of user %s was downloaded: %s", user.name, photo_file_name)
        analyze_photo(user.id, photo_file_name)

    @classmethod
    def add_friend(cls, bot, update):
        _, friend_username = update.message.text.split(maxsplit=1)
        AddFriends.add_friend(friend_username, bot, update)
