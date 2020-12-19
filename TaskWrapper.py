import spacy


class TaskWrapper(object):

    def __init__(self, text, token):
        self.text = text
        self.token = token

    def __eq__(self, other):
        if not other:
            return False
        if isinstance(self.token, spacy.tokens.span.Span) or isinstance(other.token, spacy.tokens.span.Span):
            if isinstance(self.token, spacy.tokens.span.Span) and isinstance(other.token, spacy.tokens.span.Span):
                return other.token == self.token
            elif isinstance(self.token, spacy.tokens.span.Span):
                return other.token in self.token
            else:
                return self.token in other.token
        else:
            return self.text == other.text


class EntityWrapper(TaskWrapper):

    def __init__(self, text, token):
        TaskWrapper.__init__(self, text, token)
        self.pre_connectors = []
        self.attributes = []
        self.post_connectors = []

    def __repr__(self):
        return str(self.pre_connectors) + "-->" + self.text + str(self.post_connectors)

    def add_attribute(self, attribute):
        self.attributes.append(attribute)


class AttributeWrapper(TaskWrapper):

    def __init__(self, text, token):
        TaskWrapper.__init__(self, text, token)

    def __repr__(self):
        return self.text
