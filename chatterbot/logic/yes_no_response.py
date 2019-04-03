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

        direct_question = None
        try:
            direct_question = next(generator_direct_question)
        except StopIteration:
            pass

        response_tag = ''
        response_text = ''
        generator_response = None

        if direct_question:
            if statement.text.strip('.?!/;:\'\"') in constants.AFFIRMATIVES:
                response_tag = self.get_affirmative_tag(direct_question)
            elif statement.text.strip('.?!/;:\'\"') in constants.NEGATIVES:
                response_tag = self.get_negative_tag(direct_question)

        if response_tag:
            generator_response = self.chatbot.storage.filter(text=response_tag)
            try:
                answer = next(generator_response)
                answer.confidence = 1
                return answer
            except StopIteration:
                '''
                There were occasional instances during testing where storage.filter() would return a generator object
                with no items in it, causing a StopIteration error. This happened despite there being a statement in the
                database with a matching text field. The issue was hard to reproduce. This is a workaround.
                '''
                desired_stmnt = Statement(text=response_tag)
                desired_stmnt.confidence = 1
                return desired_stmnt

        # Many direct questions are only tagged for AFF or NEG response, not both.
        # This logic adapter should still choose responses for those cases, since BestMatch will always be guessing.
        # SUGGEST response causes the chatbot to query the suggestion tree and bring up undiscussed topics.
        default_response = Statement(text='SUGGEST')
        default_response.confidence = 1
        return default_response

    @staticmethod
    def get_affirmative_tag(statement):
        tags = statement.get_tags()

        for tag in list(tags):
            if tag[:4] == 'AFF:':
                return tag[4:]

        return None

    @staticmethod
    def get_negative_tag(statement):
        tags = statement.get_tags()

        for tag in list(tags):
            if tag[:4] == 'NEG:':
                return tag[4:]

        return None
