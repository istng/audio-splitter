import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import BaseFilter, MessageHandler, Filters
import logging
import argparse
from collections import namedtuple
import audioSplitter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                       level=logging.INFO)

argumentsDescMsg  = 'Bot initialization parameters.'
tokenArgHelp      = 'telegram token'
sourceDirArgHelp  = 'audio files source directory'
outputDirArgHelp  = 'audio files output directory'

audioBotStartMsg  = 'Hello! This is the audio splitter bot.'
audioBotHelpMsg   = 'Currently this bot is under construction.'
invalidCommandMsg = 'Invalid command.'

audioTypes = ['zapada', 'ensayo']
Interval   = namedtuple('Interval', ['start', 'end'])

def parse_audio_lines(lines):
    audios_to_split = []
    for line in lines.splitlines():
        audio_line = line.split()
        to_split = dict()
        to_split['input_file']   = audio_line[0]
        to_split['intervals']    = [Interval(start=interval[0], end=interval[1]) for interval in 
                                            zip(audio_line[1::2], audio_line[2::2])]
        audios_to_split.append(to_split)
    return audios_to_split

def splitted_audio_files_reply(bot, update):   
    chat_id = update.message.chat_id
    
    audios_to_split = parse_audio_lines(update.message.text)
    
    bot.send_message(chat_id=chat_id, text='Starting to split files...')
    for audio in audios_to_split:
        bot.send_message(chat_id=chat_id, text='Splitting '+audio['input_file']) #change this to a percentage, maybe editing the message
        for interval in audio['intervals']:
            input_file  = './'+audio['input_file']
            output_file = input_file[0:-4]+'_'+interval.start+interval.end+input_file[-4::1]
            audioSplitter.split_by_intervals(audio['input_file'],
                                                    output_file,
                                                    interval.start,
                                                    interval.end)
    bot.send_message(chat_id=chat_id, text='Finished!\nDownload link: LINK') #comming soon

def invalid_command_reply(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=invalidCommandMsg)


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('token', metavar='TOKEN', type=str, help=tokenArgHelp)
    parser.add_argument('sourcedir', metavar='SOURCE DIRECTORY', type=str, help=sourceDirArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT DIRECTORY', type=str, help=outputDirArgHelp)
    args = parser.parse_args()
    return args

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=audioBotStartMsg)

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=audioBotHelpMsg)

#maybe a filter thats 'not' this to catch invalid commands...
class Filter(BaseFilter):
    def audio_type(self, message):
        msg = message.text.lower()
        for aType in audioTypes:
            if aType in msg:
                return True
        return False
    def invalid_command(self, message):
        msg = message.text.lower()
        return (not 'start' in msg) or (not 'end' in msg) or (not audio_type(msg))

def main():
    botArgs = parse_input()
    
    updater = Updater(botArgs.token)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(MessageHandler(Filter().audio_type, splitted_audio_files_reply))
    updater.dispatcher.add_handler(MessageHandler(Filter().invalid_command, invalid_command_reply))
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
