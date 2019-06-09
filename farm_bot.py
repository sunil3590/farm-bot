from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import requests
import json

host = 'http://myprojectwebservice-env.8w6stmfdbd.ap-south-1.elasticbeanstalk.com/rest/restwebservice/'


def send_command_to_waterpump(command):
    params = dict()
    params['database'] = 'pragmagprsdb'
    params['tablename'] = 'projectdata'
    params['columnnames'] = 'collegename,projectnumber,data,dataname,hasread,datatime'
    params['columnvalues'] = "'IAB','212','" + command + "','HW',0,now()"

    response = requests.get(host + 'insert', params=params)
    if response.status_code == 200:
        return True
    else:
        return False


def switch_on(bot, update):
    print('Received /switch_on command')

    success = send_command_to_waterpump('P1@')
    if success:
        update.message.reply_text('Successfully switched on the water pump')
    else:
        update.message.reply_text('There was some error while switching on.')


def switch_off(bot, update):
    print('Received /switch_off command')

    success = send_command_to_waterpump('P0@')
    if success:
        update.message.reply_text('Successfully switched off the water pump')
    else:
        update.message.reply_text('There was some error while switching off.')


def details(bot, update):
    print('Received /details command')

    params = dict()
    params['database'] = 'pragmagprsdb'
    params['tablename'] = 'projectdata'
    params['columns'] = "date(datatime) as Date,DATE_FORMAT(DATE_ADD(datatime, INTERVAL 6 HOUR)," \
                        "GET_FORMAT(TIME,'EUR')) as time,substring(data,2,3),substring(data,6,1)," \
                        "substring(data,8,1),substring(data,10,1)"
    params['conditions'] = "hasread='3' AND collegename ='IAB' AND projectnumber ='212'"

    response = requests.get(host + 'select', params=params)
    if response.status_code != 200:
        update.message.reply_text('There was some error while fetching details.')

    update.message.reply_text('Here are the details')
    update.message.reply_text(str(['Date', 'Time', 'Soil', 'Rain', 'Pump', 'Motion']))

    count = 0
    js = json.loads(response.text)
    for row in js.values():
        update.message.reply_html(str(row))
        count += 1
        if count == 5:
            break


def text_handler(bot, update):
    print('Received an update')
    # update.message.text.upper()
    update.message.reply_text('Please select one of the following commands'
                              '\n/details\n/switch_on\n/switch_off')


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater('')  # TODO

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("details", details))
    dp.add_handler(CommandHandler("switch_on", switch_on))
    dp.add_handler(CommandHandler("switch_off", switch_off))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    # Start the Bot
    print('Farm Bot started')
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
