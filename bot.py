#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "mahdikh6@gmail.com (mehrad 'Bosbaba' alizadeh)"

import logging, re, requests, os
from telegram.ext   import Updater, CommandHandler, MessageHandler
from telegram.ext   import Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async

VERSION     = '0.1'
FILES_POOL  = '/tmp/'
CONFIG_FILE = 'conf/token.conf'

logging.basicConfig (format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger (__name__)

try:
    TOKEN   = open (CONFIG_FILE, 'r').read ().replace ("\n", "")
except Exception as e:
    logger.error ("Could not find '%s'." %(CONFIG_FILE))
    exit (1)

def remove (filename):
    """ Removes the file after transfer.
    """
    try:
        os.remove (FILES_POOL + filename)
    except Exception as e:
        logger.error ("Something went wrong, backtrace: \n%s" %(e))
        return
    logger.info ("Removed %s", filename)

def transfer (filename):
    """ Sends filename then calls remove to delete it. Returns transfer.sh file's url.
    """
    upload_url = "https://transfer.sh/" + filename
    try:
        #   Upload file
        req = requests.put (url=upload_url, data=open (FILES_POOL + filename, "r"))
    except Exception as e:
        logger.error ("Something went wrong, backtrace: \n%s" %(e))
        return (e)
    logger.info ("Transferred %s", filename)
    remove (filename)
    try:
        #   Request shall return 'https://transfer.sh/AAAA/filename'
        return (req.text.strip ())
    except Exception as e:
        logger.error ("Something went wrong, backtrace: \n%s" %(e))
        return (e)

def download (document, filename):
    """ Downloads attachment
    """
    try:
        document.download (FILES_POOL + filename)
    except Exception as e:
        logger.error ("Something went wrong, backtrace: \n%s" %(e))
        return False
    return True

def checkSize (filesize, update):
    """ Checks if filesize fits inside 20mb. True if it does
    """
    SIZE_LIMIT = 20971520
    if (filesize > SIZE_LIMIT):
        update.message.reply_text ("Your file is too big! Size limited to 20mb by Telegram Bot API", quote=True)
        logger.warn ("Rejected file, size was %s" %(filesize))
        return False
    return True

#   HANDLERS
def cmd_start (bot, update):
    """ Send a message when the command /start is issued.
    """
    update.message.reply_text ('Transferbot ' + VERSION)
    update.message.reply_text ('Just send a picture, video, song or any other of telegram-supported ' \
                               'media to upload it over transfer.sh')

def cmd_help (bot, update):
    """ Send a message when the command /help is issued.
    """
    update.message.reply_text ('Just send a picture, video, song or any other of telegram-supported ' \
                               'media to upload it over transfer.sh')

def cmd_unknown (bot, update):
    """ Send a message if the command is not defined.
    """
    update.message.reply_text ('Command not found. Type /help.')

def cmd_error (bot, update, error):
    """ Log Errors caused by updates.
    """
    logger.warning ('Update "%s" caused error "%s"', update, error)

#   ATTACHMENTS MGMT
@run_async
def fbk_document (bot, update):
    """ Get document, then transfer it.
    """
    if (checkSize (update.message.document.file_size, update)):
        user        = update.message.from_user
        document    = bot.get_file (update.message.document.file_id)
        if (download (document, update.message.document.file_name)):
            logger.info ("Got document from %s: %s", user.username, update.message.document.file_name)
            update.message.reply_text ('Your transfer.sh link: ' + transfer (update.message.document.file_name),
                    quote=True)

@run_async
def fbk_audio (bot, update):
    """ Get audio, then transfer it.
    """
    if (checkSize (update.message.audio.file_size, update)):
        FIRST_EMT   = 0
        ext         = re.findall (r'/(\w+)', update.message.audio.mime_type)[FIRST_EMT]
        filename    = update.message.audio.file_id + '.' + ext
        user        = update.message.from_user
        document    = bot.get_file (update.message.audio.file_id)
        if (download (document, filename)):
            logger.info ("Got audio from %s: %s", user.username, filename)
            update.message.reply_text ('Your transfer.sh link: ' + transfer (filename),
                    quote=True)

@run_async
def fbk_voice (bot, update):
    """ Get audio, then transfer it.
    """
    if (checkSize (update.message.voice.file_size, update)):
        FIRST_EMT   = 0
        ext         = re.findall (r'/(\w+)', update.message.voice.mime_type)[FIRST_EMT]
        filename    = update.message.voice.file_id + '.' + ext
        user        = update.message.from_user
        document    = bot.get_file (update.message.voice.file_id)
        if (download (document, filename)):
            logger.info ("Got voice from %s: %s", user.username, filename)
            update.message.reply_text ('Your transfer.sh link: ' + transfer (filename),
                    quote=True)

@run_async
def fbk_video (bot, update):
    """ Get video, then transfer it.
    """
    if (checkSize (update.message.video.file_size, update)):
        FIRST_EMT   = 0
        ext         = re.findall (r'/(\w+)', update.message.video.mime_type)[FIRST_EMT]
        filename    = update.message.video.file_id + '.' + ext
        user        = update.message.from_user
        document    = bot.get_file (update.message.video.file_id)
        if (download (document, filename)):
            logger.info ("Got video from %s: %s", user.username, filename)
            update.message.reply_text ('Your transfer.sh link: ' + transfer (filename),
                    quote=True)

@run_async
def fbk_photo (bot, update):
    """ Get chat photo, the biggest from the list
    """
    #   Get the last picture of the set, highest resolution
    pic_index   = len (update.message.photo) - 1
    if (checkSize (update.message.photo[pic_index].file_size, update)):
        filename    = update.message.photo[pic_index].file_id + '.jpg'
        user        = update.message.from_user
        document    = bot.get_file (update.message.photo[pic_index].file_id)
        if (download (document, filename)):
            logger.info ("Got photo from %s: %s", user.username, filename)
            update.message.reply_text ('Your transfer.sh link: ' + transfer (filename),
                    quote=True)

#   MAIN
def main ():
    """ Start the bot.
    """
    #   Create the EventHandler and pass it your bot's token.
    updater = Updater (TOKEN)

    #   Get the dispatcher to register handlers
    dp = updater.dispatcher

    #   On different commands - answer in Telegram
    dp.add_handler (CommandHandler ("start",        cmd_start))
    dp.add_handler (CommandHandler ("help",         cmd_help))

    #   On unknown command, put some help text
    dp.add_handler (MessageHandler (Filters.command,    cmd_unknown))

    #   We don't need text interactions, give /help instead
    dp.add_handler (MessageHandler (Filters.text,       cmd_help))

    #   Add stuff to handle
    dp.add_handler (MessageHandler (Filters.photo,      fbk_photo))
    dp.add_handler (MessageHandler (Filters.audio,      fbk_audio))
    dp.add_handler (MessageHandler (Filters.voice,      fbk_voice))
    dp.add_handler (MessageHandler (Filters.video,      fbk_video))
    dp.add_handler (MessageHandler (Filters.document,   fbk_document))

    #   log all errors
    dp.add_error_handler (cmd_error)

    #   Start the Bot
    updater.start_polling ()
    logger.info ('Kicking')

    #   Loop until SIGNALS
    updater.idle ()

if __name__ == '__main__':
    main ()
