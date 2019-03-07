import logging
from chatterbot import ChatBot
from chatterbot.trainers import CustomCorpusTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import constants

# suppress unimportant warnings from getting in the way of conversation in the terminal.
logging.basicConfig(level=logging.CRITICAL)

chatbot = ChatBot('alice',
                  logic_adapters=[
                      "chatterbot.logic.YesNoLogicAdapter",
                      "chatterbot.logic.BestMatch"
                  ])

chatbot.read_only = True

trainer = CustomCorpusTrainer(chatbot)
trainer.train(
    './training_corpus/account.yml',
    './training_corpus/initial_meeting.yml',
    './training_corpus/phone.yml'
)

# Basic conversation loop based on official ChatterBot quickstart guide
while True:
    try:
        print('You: ', end='')
        user_input = input()

        if user_input in constants.END_STRINGS:
            print('Bot: Farewell.')
            break

        bot_response = chatbot.get_response(user_input)
        print('Bot: ', bot_response)

    except(KeyboardInterrupt, EOFError, SystemExit):
        break
