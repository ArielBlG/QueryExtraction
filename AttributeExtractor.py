from nltk.corpus import stopwords
import spacy

stopwords = stopwords.words('english')


class Attribute(object):

    def __init__(self, entity, dependency, attribute):
        self.entity = entity
        self.dependency = dependency
        self.attribute = attribute

    def __repr__(self):
        return "( " + self.entity.token.text \
               + ' ' + self.attribute.token.text + " ) " \
               + "Dependency: " + self.dependency

    def __eq__(self, other):
        return (
                (self.entity.token.text == other.attribute.token.text)
                and (other.entity.token.text == self.attribute.token.text)
                and (self.dependency == other.dependency))


def stop_words_finder(first_vertex, second_vertex):
    return (first_vertex.token.text.lower() in stopwords) or (second_vertex.token.text.lower() in stopwords)


def punct_finder(first_vertex, second_vertex):
    return (first_vertex.token.is_punct or second_vertex.token.is_punct) \
           or (first_vertex.token.is_left_punct or second_vertex.token.is_left_punct) \
           or (first_vertex.token.is_right_punct or second_vertex.token.is_right_punct)


class AttributeExtractor:

    def __init__(self, text, dep_graph, ent_list, doc, entity_dict):
        self._text = text
        self._doc = doc
        self.dep_graph = dep_graph
        self.entity_list = ent_list
        self.entity_dict = entity_dict
        self._attributes = []

    def initiate_extractor(self):
        self.Rule_1("advmod")
        self.Rule_1("amod")
        self.Rule_1("nummod")
        self.Rule_1("nmod")
        # print(self._attributes)

    def Rule_1(self, dependency):
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                for edge in vertex.get_edge_by_dep_iter(dependency):
                    if edge is not None:
                        if not stop_words_finder(vertex, edge.target) and not punct_finder(vertex, edge.target):
                            attribute = Attribute(vertex, dependency, edge.target)
                            if attribute not in self._attributes:
                                vertex.attributes.append(attribute)
                                self._attributes.append(attribute)
                                self.entity_dict[vertex.token.text] = self.get_span(edge.target.token,
                                                                                    self.entity_dict[vertex.token.text],
                                                                                    vertex_token=vertex.token)
                                if edge.target.token.text in self.entity_dict:
                                    self.entity_dict[edge.target.token.text] = self.entity_dict[vertex.token.text]
                                # print(self.entity_dict[vertex.token.text].text)

    def get_current_token(self, comp_list, vertex_token):
        for comp in comp_list:
            if self._doc[vertex_token.i:vertex_token.i+1] == comp:
                return comp

    def get_span(self, entity, comp=None, vertex_token=None):
        """
        :param vertex_token:
        :param entity:
        :param comp:
        :return:
        """
        if isinstance(comp, list):
            comp = self.get_current_token(comp, vertex_token)
        if isinstance(comp, spacy.tokens.span.Span):
            if entity.i < comp.end:
                return self._doc[entity.i: comp.end]
            else:
                return self._doc[comp.end - 1: entity.i + 1]
        else:
            if entity.i < comp.i:
                return self._doc[entity.i:comp.i + 1]
            else:
                return self._doc[comp.i:entity.i + 1]
