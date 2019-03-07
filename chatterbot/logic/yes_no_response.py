from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import constants


class YesNoLogicAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        stmnt_text = statement.text.strip('.?!/;:\'\"')

        if stmnt_text in constants.AFFIRMATIVES:
            return True
        elif stmnt_text in constants.NEGATIVES:
            return True
        else:
            return False

    def process(self, statement, additional_response_selection_parameters=None):
        """
        Given an affirmative/negative statement from the user:
            1. Detect which question from the bot the user in answering.
            2. Return appropriate response to the user.

        """

        # I found the following three lines to be necessary after quite a bit of debugging.
        # get_last() returns a Statement object with all fields empty except for text and created_at.
        # When chatbot.storage.filter() is used it returns a generator object, not a Statement object.
        # Using next() on the generator object gets us the desired Statement object with all needed data.
        incomplete_direct_question = self.chatbot.get_last()
        generator_direct_question = self.chatbot.storage.filter(text=incomplete_direct_question.text)
        direct_question = next(generator_direct_question)

        response_tag = ''
        response_text = ''
        generator_response = None

        if direct_question:
            if statement.text.strip('.?!/;:\'\"') in constants.AFFIRMATIVES:
                response_tag = self.get_affirmative_tag(direct_question)
            elif statement.text.strip('.?!/;:\'\"') in constants.NEGATIVES:
                response_tag = self.get_negative_tag(direct_question)

        if response_tag:
            response_tag = response_tag[4:]
            generator_response = self.chatbot.storage.filter(text=str(response_tag))

        if generator_response:
            # next() is needed to get text from the generator object.
            response_text = next(generator_response).text
            generator_answers = self.chatbot.storage.filter(text=response_text)
            answer = next(generator_answers)
            answer.confidence = 1
            return answer

        direct_question.confidence = 0
        return direct_question

    @staticmethod
    def get_affirmative_tag(statement):
        tags = statement.get_tags()

        for tag in list(tags):
            if tag[:4] == 'AFF:':
                return tag

        return None

    @staticmethod
    def get_negative_tag(statement):
        tags = statement.get_tags()

        for tag in list(tags):
            if tag[:4] == 'NEG:':
                return tag

        return None
