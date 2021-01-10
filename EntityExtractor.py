import TaskWrapper
import spacy
from newDepGraph import Node, Vertex, Edge
from SpaCyUtils import is_noun, get_compound_nouns, get_nouns, get_nouns_span

problem_words = ["to", "end", "of", "in", "java", "Java"]


class EntityExtractor:

    def __init__(self, text, dep_graph, ent_list, doc):
        """

        :param text:
        :param dep_graph:
        :param ent_list:
        :param doc:
        """
        self._text = text
        self._doc = doc
        self.dep_graph = dep_graph
        self.entity_list = ent_list
        self.entity_after_filter = []
        self.comp_nouns = None
        self.nouns = None
        self.entity_dict = {}

    def init_extraction(self):
        """

        :return:
        """
        self.create_graph()
        self.filter_entities()
        self.get_comp_nouns_from_text()
        self.get_nouns_from_text()
        self.get_entities_from_nouns()
        self.get_entities_from_comp()
        self.entity_to_dict()

    def entity_to_dict(self):
        for entity in self.entity_after_filter:
            for token in entity:
                if token.text not in self.entity_dict.keys():
                    self.entity_dict[token.text] = entity
                else:
                    if entity != self.entity_dict[token.text]:
                        if isinstance(self.entity_dict[token.text], list):
                            self.entity_dict[token.text].append(entity)
                        else:
                            curr_ent = self.entity_dict[token.text]
                            self.entity_dict[token.text] = [curr_ent, entity]

    def get_entities_from_nouns(self):
        entities = list(set(self.entity_after_filter).union(self.nouns))
        new_entities = [entity for entity in entities if entity.text not in problem_words]
        self.entity_after_filter = new_entities

    def get_entities_from_comp(self):
        """

        :return:
        """
        entities = []
        for entity in self.entity_after_filter:
            contains, comp_noun = self.find_entity_in_comp(entity)
            if not contains:
                curr_ent = self.get_span(entity)
                if curr_ent not in entities:
                    entities.append(curr_ent)
            else:
                curr_ent = self.get_span(comp_noun[0], comp_noun[1])
                if curr_ent not in entities:
                    entities.append(curr_ent)
        self.entity_after_filter = entities

    def find_entity_in_comp(self, entity):
        """

        :param entity:
        :return:
        """
        for comp_noun in self.comp_nouns:
            if entity in comp_noun:
                return True, comp_noun
        return False, None

    def get_span(self, entity, comp=None):
        """

        :param entity:
        :param comp:
        :return:
        """
        if not comp:
            return self._doc[entity.i:entity.i + 1]
        else:
            if entity.i < comp.i:
                return self._doc[entity.i:comp.i + 1]
            else:
                return self._doc[comp.i:entity.i + 1]

    def filter_entities(self):
        """

        :return:
        """
        for entity in self.entity_list:
            if entity.text not in problem_words:
                self.entity_after_filter.append(entity.root)

    def create_graph(self):
        """

        :return:
        """
        print("***** Dependency Graph *****")
        for token in self._doc:

            print(token.dep_ + '(' + token.text + ',' + token.head.text + ')')
            print(token.text + "-" + token.pos_)

            first_vertex = self.dep_graph.get_vertex(token)
            if first_vertex is None:
                first_vertex = Vertex(token)
                self.dep_graph.insert(first_vertex)
            second_vertex = self.dep_graph.get_vertex(token.head)
            if second_vertex is None:
                second_vertex = Vertex(token.head)
                self.dep_graph.insert(second_vertex)
            self.dep_graph.new_edge(first_vertex, second_vertex, token.dep_)
        # print("***** Relationships *****")

    def get_comp_nouns_from_text(self):
        """

        :return:
        """
        self.comp_nouns = (get_compound_nouns(self._text, self._doc))

    def get_nouns_from_text(self):
        """

        :return:
        """
        self.nouns = (get_nouns(self._doc))
