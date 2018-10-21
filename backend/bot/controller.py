from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.update import Update
from telegram.utils.promise import Promise
from telegram.ext import (
    Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, RegexHandler,
    Job
)
import logging
from .analyze_photo import analyze_photo

from .settings import MIN_FRIEND_COUNT, TOKEN
import os
from datetime import timedelta
from api.get_score import browser_history_score_info, twitter_score_info, detect_depression
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()
from api.models import User
from collections import namedtuple
from .quest import *
Url = namedtuple('Url', ['url', 'ts'])


def get_urls():
    return [
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+wanna+dance+with+somebody+and+be+happy+I+happy&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+dance+with+somebody+and+be+happy+I+happy&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+wanna+sing+with+somebody+and+be+happy+I+happy&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+believe+in+love&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+wanna+swim&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.google.es/search?hl=ru&source=hp&ei=yqjLW4bvCYPqrgSNrLL4CA&q=i+love+my+mom&oq=i+wanna+dance+with+somebody+and+be+happy+I+happy&gs_l=psy-ab.3..33i160k1l2.78913.95588.0.97926.37.32.4.1.1.0.138.3109.16j15.31.0....0...1c.1.64.psy-ab..1.35.3014...0j0i22i30k1j0i19k1j0i22i30i19k1j33i22i29i30k1j33i21k1.0.Qpf975be7AE', ts=1540048662161.8308),
        Url(url='https://www.charliechaplin.com/it/articles/42-Smile-Lyrics', ts=1540148662161.8308),
        Url(url='https://en.wikipedia.org/wiki/Happiness', ts=1540047662161.8308),
        Url(url='https://en.wikipedia.org/wiki/Lions', ts=1540047362161.8308),
        Url(url='https://en.wikipedia.org/wiki/Sadness', ts=1540047962161.8308),
    ]


MY_URL = "https://chrome.google.com/webstore/detail/depression-is-weaker-than/afglhfhcelehgbbhpefplibhgkkjgjck?depressionweakerthan_user_id={}"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_all_subscribers(user_id):
    user = User.objects.get(user_id=user_id)
    return [friend.user_id for friend in user.trusted.all() if friend.user_id is not None]


def get_all_subscriptions(user_id):
    user = User.objects.get(user_id=user_id)
    return [friend.user_id for friend in user.user_set.all() if friend.user_id is not None]


def get_user_by_username(username):
    return User.objects.get(username=username)


def get_subscribers_count(user_id):
    return User.objects.get(user_id=user_id).trusted.count()


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
            friend_username = '@' + friend_username
        logger.info('User {} want to add friend {}'.format(user.id, friend_username))
        friend = User.objects.filter(username=friend_username).first()
        if friend is None:
            friend = User(username=friend_username)
            friend.save()
        if friend.user_id is None:
            update.message.reply_text(
                ("I don't know {} yet. Please share link "
                "t.me/depression_weaker_than_tech_bot with them. "
                "When they register, I will be able to notify them of your status").format(friend_username)
            )
            logger.info('Not found friend with username: {}'.format(friend_username))
        else:
            add_friend_message = (
                'User {} has added you to their list of trusted friends. '
                'Now I will drop you a message should they need your attention and care'
            )
            bot.send_message(
                friend.user_id,
                add_friend_message.format(user.name)
            )
            update.message.reply_text(
                'User {} was added to list of your trusted friends.'.format(friend_username)
            )

            logger.info('Found friend id: ' + str(friend.user_id))
        User.objects.get(user_id=user.id).trusted.add(friend)
        return True

    @classmethod
    def add_subscriber(cls, bot, update):
        friend_username = update.message.text
        if not AddFriends.add_friend(friend_username, bot, update):
            return AddFriends.name

        user_id = update.message.from_user.id
        curr_friends_count = get_subscribers_count(user_id)

        if curr_friends_count >= MIN_FRIEND_COUNT:
            reply_markup = ReplyKeyboardMarkup([[cls._done]], one_time_keyboard=True)
            update.message.reply_text(
                ('If you wish, you can now add more friends. '
                'When you are finished, press "Done" button. '
                'You will also be able to add more friends later.').format(friend_username),
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
            'To help me monitor your browsing habits, please add my Chrome extention:\n' +
            MY_URL.format(update.message.from_user.id) + '\n'
            "Don't worry, I will not gather any information except for aggregated numerical "
            "statistics. Sites you visit or any other sensitive data is not stored.",
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
            'Great! Could you tell me your Twitter username? '
            'I will calculate statistics based on your posts and likes.'
            'If you don\'t use Twitter or don\'t want to share it with me, '
            'just press "' + AddTwitter.skip_message + '".',
            reply_markup=ReplyKeyboardMarkup([[AddTwitter.skip_message]], one_time_keyboard=True)
        )
        user_object = User.objects.get(user_id=update.message.from_user.id)
        urls = user_object.url_set.order_by("-ts")
        # urls = get_urls()
        result = browser_history_score_info(urls)
        logger.info('Got user {} browser history, stats: {}'.format(user_object.username, result))
        user_object.url_week_score = result['avg_week_score'][-1]
        user_object.url_month_score = result['avg_month_score']
        user_object.save()
        return AddTwitter.name


class AddTwitter(Stage):
    name = "ADD_TWITTER"
    skip_message = 'Skip'
    end_message = (
        "That's all for now, thanks! I will monitor your activity and ping your friends if I think you need extra care."
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
        user_id = update.message.from_user.id
        user = User.objects.filter(user_id=user_id).first()
        if not user.activated:
            logger.info('Run monitorings for user with id=' + str(user_id))
            Job(
                Controller.ask_for_photo, interval=timedelta(0, 40),
                context={'user_id': user_id}
            ).run(bot)
            Job(Controller.grab_stat, interval=timedelta(1), context={'user_id': user_id}).run(bot)
            user.activated = True
            user.save()
        return ConversationHandler.END

    @classmethod
    def enter_twitter_login(cls, bot, update):
        user_id = update.message.from_user.id
        login = update.message.text
        user = User.objects.filter(user_id=user_id).first()
        user.twitter_login = login
        user.save()
        logger.info('User {} add twitter login {}'.format(user.username, login))
        res = twitter_score_info(login)
        user.twitter_month_score = res['avg_month_score']
        user.twitter_week_score = res['avg_week_score'][-1]
        user.save()
        logger.info('Got twitter depression score of user {}: {}'.format(user.username, res))
        update.message.reply_text(cls.end_message, reply_markup=ReplyKeyboardRemove())
        if not user.activated:
            logger.info('Run monitorings for user with id=' + str(user_id))
            Job(
                Controller.ask_for_photo, interval=timedelta(0, 40),
                context={'user_id': user_id}
            ).run(bot)
            Job(Controller.grab_stat, interval=timedelta(1), context={'user_id': user_id}).run(bot)
            user.activated = True
            user.save()
        return ConversationHandler.END


class Controller:
    DEPRESSED = "/i_m_depressed"
    ADD_FRIEND = '/add_friend'
    HELP = '/help'
    REGISTER = '/register'
    QUEST = '/quest'

    STATE = {
    }

    @classmethod
    def run_bot(cls):
        cls._updater = Updater(TOKEN)
        dispatcher = cls._updater.dispatcher

        meeting_conversation_stages = [AddFriends, AddExtention, AddTwitter, ]
        meeting_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('register', cls.register)],
            states={stage.name: stage.get_handlers() for stage in meeting_conversation_stages},
            fallbacks=[],
        )
        dispatcher.add_handler(meeting_conversation_handler)

        quest_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('quest', cls.start_quest)],
            states={"select": [MessageHandler(Filters.text, cls.select_perspective)], "quest": [MessageHandler(Filters.text, cls.quest)]},
            fallbacks=[],
        )
        dispatcher.add_handler(quest_conversation_handler)

        dispatcher.add_handler(CommandHandler('start', cls.start_meeting))
        dispatcher.add_handler(CommandHandler(
            cls.DEPRESSED[1:],
            lambda bot, update: cls.notify_friends_about_depression(update.message.from_user.id)
        ))
        dispatcher.add_handler(CommandHandler(cls.HELP[1:], cls.print_help))
        dispatcher.add_handler(CommandHandler(cls.ADD_FRIEND[1:], cls.add_friend))
        dispatcher.add_handler(MessageHandler(Filters.photo, cls.analyze_photo))
        dispatcher.add_handler(CommandHandler('_grab_stat', cls.grab_stat))

        bot = cls.get_bot()
        for user_object in User.objects.all():
            if not user_object.activated:
                continue
            user_id = user_object.user_id
            logger.info('Run monitorings for user with id=' + str(user_id))
            Job(
                cls.ask_for_photo, interval=timedelta(0, 40),
                context={'user_id': user_id}
            ).run(bot)
            Job(cls.grab_stat, interval=timedelta(1), context={'user_id': user_id}).run(bot)

        cls._updater.start_polling()
        cls._updater.idle()

    @classmethod
    def start_meeting(cls, bot, update):
        user = User.objects.filter(username=update.message.from_user.name).first()
        if not user:
            user = User(username=update.message.from_user.name)
        user.user_id = update.message.from_user.id
        user.save()

        update.message.reply_text('Hi!')

        update.message.reply_text(
            "I can help self-diagnose and fight mild cases of depression "
            "by informing your friends that you need care.\n"
            "You can learn more about me here: http://depressionweakerthan.tech. \n"
            "If you want, you can just lurk and recieve notifications about your friends' statuses. "
            "However, I strongly recommend you to add trusted friends and install my browser extension. "
            "It is a good idea to take care of yourself even if you don't think you could ever get depressed.\n"
        )

        subscriptions = get_all_subscriptions(update.message.from_user.id)
        for subscription in subscriptions:
            update.message.reply_text(
                'User {} has added you as trusted friend'.format(cls.get_username(subscription))
            )
        update.message.reply_text("Type /help to get a list of all avaliable commands.")

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
        cls.notify_friends_about_depression(user_id)
        cls.notify_user_about_depression(user_id)

    @classmethod
    def notify_user_about_depression(cls, user_id):
        bot = cls.get_bot()
        bot.send_message(
            user_id,
            "I'm worring about your recent Internet activity. "
            "Honestly, I think you are a little bit depressed! :(\n"
            "Try to relax and talk to your friends about your feelings. I hope, you will cheer up!"
        )

    @classmethod
    def notify_friends_about_depression(cls, user_id):
        bot = cls.get_bot()
        username = cls.get_username(user_id)
        for subscriber in get_all_subscribers(user_id):
            bot.send_message(
                subscriber,
                'I noticed that your friend, ' + username +
                ', is feeling a little bit unhappy lately. '
                'You should talk to them and ask about their feelings.'
            )

    @classmethod
    def print_help(cls, bot, update):
        update.message.reply_text(
            'Type ' + cls.HELP + ' to get help (prints this message).\n'
            'Type ' + cls.QUEST + ' to play my small game about depression.\n'
            'Type /register to allow me monitor your mental wellness, if you have not already.\n'
            'Type ' + cls.DEPRESSED + ' to tell your freinds that your is depressed.\n'
            'Type "' + cls.ADD_FRIEND + ' @friend_username" to add person with username '
            '@friend_username to your friends. He or she will be notified if I somehow '
            'realize that you are depressed.\n'
            'Also you can send me your photo. It also'
            ' helps me to predict whether you depressed or not.\n'
        )

    @classmethod
    def analyze_photo(cls, bot, update):
        photo_file = bot.get_file(update.message.photo[-1].file_id)
        user = update.message.from_user
        photo_file_name = '{}_photo.jpg'.format(user.name)
        photo_file.download(photo_file_name)
        logger.info("Photo of user %s was downloaded: %s", user.name, photo_file_name)
        try:
            scores = analyze_photo(photo_file_name)
        except ValueError as e:
            update.message.reply_text("I can't find any face on this photo :(")
            return
        logger.info(photo_file_name + ' scores: ' + str(scores))
        if scores['sadness'] > 0.5:
            cls.notify_friends_about_depression(user.id)
            update.message.reply_text(
                "Not the greatest day, is it? Anyway, keep your chin up! "
                "Waiting for the next photo :)"
            )
        else:
            update.message.reply_text('Nice photo! Now I\'m looking forward for the next one :)')

    @classmethod
    def add_friend(cls, bot, update):
        splited_message = update.message.text.split(maxsplit=1)
        if len(splited_message) < 2:
            update.message.reply_text(
                'You should pass to this command your friend username, like this:\n' +
                cls.ADD_FRIEND + ' @friend_username'
            )
        else:
            friend_username = splited_message[1]
            AddFriends.add_friend(friend_username, bot, update)

    @classmethod
    def ask_for_photo(cls, bot, job):
        user_id = job.context['user_id']
        print(job.context)
        print(user_id)
        logger.info('Send photo request to user with id=' + str(user_id))
        bot.send_message(user_id, 'Send me a photo, please!')

    @classmethod
    def register(cls, bot, update):
        update.message.reply_text(
            "Now you can tell me username of a person whom you trust. "
            "They will be notified if you ever get depressed. "
            "You can add any number of friends, but enter one username at a time. "
        )

        return AddFriends.name

    @classmethod
    def start_quest(cls, bot, update):
        game = Game()
        cls.STATE[update.message.from_user.id] = game
        update.message.reply_text(game.start(), reply_markup=ReplyKeyboardMarkup([["Healthy"], ["Depressive"]], one_time_keyboard=True))
        return "select"

    @classmethod
    def select_perspective(cls, bot, update):
        desc = cls.STATE[update.message.from_user.id].select_perspective(update.message.text)
        update.message.reply_text("Let's start the game")
        update.message.reply_text(desc)
        update.message.reply_text("Select, where you want to spend next couple of hours",
                                  reply_markup=ReplyKeyboardMarkup([["Bed"], ["Kitchen"], ["School"]], one_time_keyboard=True))
        return "quest"

    @classmethod
    def quest(cls, bot, update):
        desc = cls.STATE[update.message.from_user.id].take_move(update.message.text)
        game = cls.STATE[update.message.from_user.id]
        if cls.STATE[update.message.from_user.id].time == 3:
            update.message.reply_text(desc)
            if game.finished:
                update.message.reply_text("Thank you for playing! You can see now that depression can affect your state. You should register now to get help when you need it.")
                return -1
            else:
                update.message.reply_text("Thats all! Now it is time to live the same day from the other perspective.")
                game.finished = 1
                game.state = "Bed"
                game.time = 0
                game.positive = not game.positive
        update.message.reply_text(game.get_description())
        update.message.reply_text("Select, where you want to spend next couple of hours",
                                  reply_markup=ReplyKeyboardMarkup([["Bed"], ["Kitchen"], ["School"]], one_time_keyboard=True))
        return "quest"

    @classmethod
    def grab_stat(cls, bot, job_or_update):
        if isinstance(job_or_update, Job):
            user_id = job_or_update.context['user_id']
        elif isinstance(job_or_update, Update):
            user_id = job_or_update.message.from_user.id
        else:
            raise ValueError('job_or_update should be Updater or Job')
        user = User.objects.filter(user_id=user_id).first()
        login = user.twitter_login
        if login is not None:
            today_twitter_score = twitter_score_info(login, deep_days=1)['avg_month_score']
            user.twitter_month_score *= 29.0 / 30.0
            user.twitter_month_score += today_twitter_score / 30.0
            user.twitter_week_score *= 6.0 / 7.0
            user.twitter_week_score += today_twitter_score / 7.0

        urls = user.url_set.order_by("-ts")
        # urls = get_urls()
        today_url_score = browser_history_score_info(urls, deep_days=1)['avg_month_score']
        user.url_month_score *= 29.0 / 30.0
        user.url_month_score += today_url_score / 30.0
        user.url_week_score *= 6.0 / 7.0
        user.url_week_score += today_url_score / 7.0

        user.save()
        logger.info('Got stat for user ' + user.username)
        is_depressed = detect_depression(
            user.url_month_score, user.url_week_score,
            user.twitter_month_score, user.twitter_week_score
        )
        if isinstance(job_or_update, Update):
            job_or_update.message.reply_text(("Here is some stats about you:\n"
                "Browsing score: {} this month, {} this week\n"
                "Twitter score: {} this month, {} this week").format(
                    user.url_month_score, user.url_week_score,
                    user.twitter_month_score or 0, user.twitter_week_score or 0))
        if is_depressed:
            logger.info('User {} is depressed'.format(user.username))
            cls.depression_detected(user_id)
