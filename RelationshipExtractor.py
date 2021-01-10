import spacy

from SpaCyUtils import is_subject, is_verb, is_adp, is_part, get_token_from_span, is_adv, is_conj
from TaskWrapper import EntityWrapper, AttributeWrapper
from RelationshipGraph import *
from newDepGraph import Graph
import networkx as nx


class Relation(object):

    def __init__(self, token=None, connected_token=None, second_connector=None, first_connector=None):
        self.token = token
        self.connected_token = connected_token
        self.first_connector = first_connector
        self.second_connector = second_connector

    def __repr__(self):
        return ' ( ' + str(self.first_connector) + ' ) ' + \
               str(self.token) + ' ( ' + \
               str(self.second_connector) + ' ) ' + \
               str(self.connected_token)

    def connection_backwards(self, relation):
        try:
            return self.token == relation.connected_token \
                   and self.first_connector == relation.second_connector \
                   and self.connected_token == relation.token \
                   and self.second_connector == relation.first_connector
        except TypeError:
            pass


def rule_2_edge(vertex):
    new_edge_list = []
    prep_edge = vertex.get_edge_by_dep("acl")
    if prep_edge:
        new_edge_list += prep_edge
    prep_edge = vertex.get_edge_by_dep("advcl")
    if prep_edge:
        new_edge_list += prep_edge
    prep_edge = vertex.get_edge_by_dep("nsubj")
    if prep_edge:
        new_edge_list += prep_edge
    prep_edge = vertex.get_edge_by_dep("relcl")
    if prep_edge:
        new_edge_list += prep_edge
    return new_edge_list


class RelationshipExtractor:

    def __init__(self, text, dep_graph, ent_list, doc, entity_dict):
        self._text = text
        self._doc = doc
        self.dep_graph = dep_graph
        self.entity_list = ent_list
        self.entity_dict = entity_dict
        self.relation_list = []
        self.rule_3_to_flag = False
        self._rule_1_list = []
        self._rule_2_list = []
        self._rule_3_list = []
        self._rule_4_list = []
        self._rule_5_list = []
        self._small_rule_list = []
        self._rule_6_list = []
        self.entity_tasks = []
        self.attribute_tasks = []
        self.relation_graph = Graph()
        self.test_graph = nx.Graph()

    def init_extraction(self):
        """
        The function starts the extraction and the task convertor
        """
        self.Rule_1()
        self.Rule_2()
        self.Rule_3("xcomp", "aux")
        self.Rule_3("ccomp", "dobj")
        self.Rule_3("prep", "pobj")
        self.Rule_3("prep", "pcomp")
        self.Rule_3("xcomp", "dobj")
        self.Rule_3("conj", "dobj")
        self.Rule_3("dative", "pobj")
        # self.Rule_3("xcomp", "aux")  # TODO: test this again with new rule
        self.Rule_3("advcl", "dobj")
        # self.Rule_3("advcl", "prep") # How to replace HashMap values while iterating over them in Java
        self.Rule_3("agent", "pobj")
        self.Rule4()
        self.Rule_5()
        self.Rule_6()  # handle and
        self.Rule_7()
        self.Rule_small()
        self.remove_unneeded_relation()
        # print(self.relation_list)
        self.relation2task(self._rule_3_list)
        self.relation2task(self._rule_5_list)
        self.relation2task(self._rule_1_list)
        self.relation2task(self._rule_4_list)
        self.relation2task(self._rule_2_list)
        self.relation2task(self._rule_6_list)
        self.relation2task(self._small_rule_list)
        print("************** Relationship Graph **************")
        for vertex in self.relation_graph:
            print(vertex)
        print("************** Task Relationships **************")
        for entity in self.entity_tasks:
            print(entity)

    def relation2task(self, recived_list):
        """
        The function converts all relation to task objects
        :param recived_list:
        """
        for rule in recived_list:
            first_connector = None
            if rule.first_connector is not None:  # Checks if there is first connector
                """check if such attribute already exists"""
                first_connector = next((x for x in self.attribute_tasks if x.text == rule.first_connector.text), None)
                if first_connector is None:  # if such attribute doesn't exists, create one
                    first_connector = AttributeWrapper(rule.first_connector.text, rule.first_connector)
                    self.attribute_tasks.append(first_connector)
            """checks if theres such entity"""
            temp_token = EntityWrapper(rule.token.text, rule.token)
            first_token = next((x for x in self.entity_tasks if x == temp_token), None)
            first_token_checker = next((x for x in self.attribute_tasks if x.text == rule.token.text), None)
            # TODO: check if its right, rule 1 token is attribute
            if first_token_checker is not None:
                continue
            if first_token is None:  # if such entity doesn't exists, create one
                first_token = EntityWrapper(rule.token.text, rule.token)
                self.entity_tasks.append(first_token)
            if first_connector is not None:  # if first connector isn't none, append to pre
                """checks if theres already such attribute connected to the entity"""
                if next((x for x in first_token.pre_connectors if x == first_connector), None) is None:
                    first_token.pre_connectors.append(first_connector)

            """check if such attribute already exists"""
            if rule.second_connector is not None:
                second_connector = next((x for x in self.attribute_tasks if x.text == rule.second_connector.text), None)
                if second_connector is None:  # if such attribute doesn't exists, create one
                    second_connector = AttributeWrapper(rule.second_connector.text, rule.second_connector)
                    self.attribute_tasks.append(second_connector)
                """checks if theres already such attribute connected to the entity"""
                if next((x for x in first_token.post_connectors if x == second_connector), None) is None:
                    first_token.post_connectors.append(second_connector)

            """checks if theres such entity"""
            temp_token = None
            if rule.connected_token is not None:
                temp_token = EntityWrapper(rule.connected_token.text, rule.connected_token)
                second_token = next((x for x in self.entity_tasks if x == temp_token), None)
                if second_token is None:  # if such entity doesn't exists, create one
                    second_token = EntityWrapper(rule.connected_token.text, rule.connected_token)
                    self.entity_tasks.append(second_token)
                """checks if theres already such attribute connected to the entity"""
                if rule.second_connector is not None:
                    if next((x for x in second_token.pre_connectors if x == second_connector), None) is None:
                        second_token.pre_connectors.append(second_connector)

    def remove_unneeded_relation(self):
        """
        The function search for unneeded relations
        :return:
        """
        len_1 = len(self._rule_1_list)
        len_2 = len(self._rule_2_list)
        len_3 = len(self._rule_3_list)
        len_4 = len(self._rule_4_list)
        len_5 = len(self._rule_5_list)
        if len_2 == 0 and len_5 == 0:
            if len_4 == 0:
                if len_1 == 1 and len_3 == 1:
                    self.relation_list.remove(self._rule_1_list.pop())
            elif len_4 == 2 or len_4 == 3:
                if len_3 >= 1:
                    for rule in self._rule_4_list:
                        self.relation_list.remove(rule)

    def Rule_1(self):
        """
        The function activates Rule 1
        prep (X,Y) + pobj (Y,Z)
        appends the extracted relation to self._rule_1_list
        """
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                prep_edge = vertex.get_edge_by_dep("prep")
                for edge in prep_edge:
                    connected_vertex = edge.target
                    second_edge = connected_vertex.get_edge_by_dep("pobj")
                    for curr_edge in second_edge:
                        if is_verb(connected_vertex.token) or is_adp(connected_vertex.token) or \
                                is_adv(connected_vertex.token):  # TODO: RULE 1 ADVERB
                            connected = self.get_current_connected(curr_edge)
                            first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
                            relation = Relation(first_ent,
                                                connected,
                                                connected_vertex.token)
                            self.relation_list.append(relation)
                            self.add_to_relation_graph(first_ent=first_ent,
                                                       connected_vertex=connected_vertex.token,
                                                       connected=connected)

                            self._rule_1_list.append(relation)
                            print("************** Rule 1 ACTIVATED **************")
                            print(relation)

    def Rule_2(self):
        """
        Rule 2 infers to vern and noun modifiers
        The function activates Rule 2
        1. acl (X,Y) + dobj (Y,Z)
        2. advcl (X,Y) + dobj (Y,Z)
        3. nsubj (X,Y) + dobj(Y,Z)
        4. relcl (X,Y) + dobj(Y,Z)
        appends the extracted relation to self._rule_2_list
        """
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                prep_edge = rule_2_edge(vertex)
                for edge in prep_edge:
                    connected_vertex = edge.target
                    scnd_edge = connected_vertex.get_edge_by_dep("dobj")
                    for second_edge in scnd_edge:
                        if is_verb(connected_vertex.token) or is_adp(connected_vertex.token):
                            first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
                            connected = self.get_current_connected(second_edge)
                            second_ent = connected
                            # second_ent = get_token_from_span(self.entity_dict[prep_edge.target.token.text],
                            #                                  prep_edge.target.token)

                            # relation = Relation(self.entity_dict[vertex.token.text],
                            #                     self.entity_dict[prep_edge.target.token.text],
                            #                     connected_vertex.token)
                            relation = Relation(first_ent,
                                                second_ent,
                                                connected_vertex.token)
                            self.relation_list.append(relation)
                            self._rule_2_list.append(relation)
                            self.add_to_relation_graph(first_ent=first_ent,
                                                       connected_vertex=connected_vertex.token,
                                                       connected=connected)

                            print("************** Rule 2 ACTIVATED **************")
                            print(relation)

    def Rule_3(self, first_dep, second_dep):
        """
        Rule 3 tries to connect between bigger modifiers dependencies
        The function activates Rule 3 by the following rules, depends on the first and second dep
        1. dobj (X,Y) + prep (Y,Z) + pobj (T,Z)
        2. dobj (X,Y) + prep (Y,Z) + pcomp (T,Z)
        3. dobj (X,Y) + xcomp (Y,Z) + dobj (T,Z)
        4. dobj (X,Y) + conj (Y,Z) + dobj (T,Z)
        5. dobj (X,Y) + dative (Y,Z) + pobj (T,Z)
        6. dobj (X,Y) + advcl (Y,Z) + dobj (T,Z)
        7. dobj (X,Y) + agent (Y,Z) + pobj (T,Z)
        8. dobj (X,Y) + xcomp (Y,Z) + aux (T,Z)
        appends the extracted relation to self._rule_2_list
        :param first_dep: first dependency node to search
        :param second_dep: second dependency node to search
        """
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                first_edge = vertex.get_edge_by_dep("dobj")
                for edge in first_edge:
                    connected_vertex = edge.target
                    scnd_edge = connected_vertex.get_edge_by_dep(first_dep)
                    first_connector = connected_vertex.token
                    if is_verb(connected_vertex.token) or is_adp(connected_vertex.token):
                        for second_edge in scnd_edge:
                            connected_vertex = second_edge.target
                            prep_edge = connected_vertex.get_edge_by_dep(second_dep)
                            second_connector = connected_vertex.token
                            if prep_edge is not None:
                                for third_edge in prep_edge:
                                    self.rule_3_it(third_edge,
                                                   connected_vertex,
                                                   vertex,
                                                   first_connector,
                                                   second_connector)

    def rule_3_it(self, prep_edge=None, connected_vertex=None, vertex=None, first_connector=None,
                  second_connector=None):
        """
        The function iterates over rule 3 extractions and finds more complicated rules
        1. dobj (X,Y) + xcomp (Y,Z) + aux (T,Z) + prep (Z, Q)
        1. dobj (X,Y) + xcomp (Y,Z) + aux (T,Z) + dobj (Z, Q)
        3. dobj (X,Y) + prep (Y,Z) + pcomp (T,Z) + dobj (Z, Q)
        :param prep_edge: edge to explore in the dependency graph
        :param connected_vertex: connected vertex represents the connected token on relation
        :param vertex: current vertex we are exploring
        :param first_connector: first connector between entities
        :param second_connector: second connector between entities
        """
        #  TODO: test it!
        if prep_edge is not None \
                and (is_verb(connected_vertex.token)
                     or is_adp(connected_vertex.token)
                     or is_part(connected_vertex.token)):
            connected = self.get_current_connected(prep_edge)
            first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
            if prep_edge.dependency == 'aux':
                prep_edge = connected_vertex.get_edge_by_dep('prep')
                if not prep_edge:
                    prep_edge = connected_vertex.get_edge_by_dep('dobj')
                for to_prep_edge in prep_edge:
                    self.rule_3_to(to_prep_edge, connected_vertex, first_ent, first_connector, connected)
                    return
            # handle pcomp
            elif prep_edge.dependency == 'pcomp':
                edge = prep_edge.target.get_edge_by_dep('dobj')
                for pcomp_edge in edge:
                    self.rule_3_to(pcomp_edge, connected_vertex, first_ent, first_connector, connected)
                    return
            self.add_to_rule_3(first_ent, connected, second_connector, first_connector)

    def rule_3_to(self, prep_edge, connected_vertex, first_ent, first_connector, connected):
        """
        The function handles "to" operations inside a text
        :param prep_edge: edge to explore in the dependency graph
        :param connected_vertex: connected vertex represents the connected token on relation
        :param first_ent: the first entity
        :param first_connector: first connector between entities
        :param connected: second connector between entities
        """
        self.rule_3_to_flag = True
        second_connector = self.get_span(connected, connected_vertex.token)
        connected_vertex = prep_edge.target
        prep_edge = connected_vertex.get_edge_by_dep('pobj')
        if prep_edge:
            for pobj_edge in prep_edge:
                connected = pobj_edge.target
                connected = self.get_span(connected_vertex.token, connected.token)
                self.add_to_rule_3(first_ent, connected, second_connector, first_connector)
        else:
            connected_vertex = self.entity_dict.get(str(connected_vertex), connected_vertex.token)
            self.add_to_rule_3(first_ent, connected_vertex, second_connector, first_connector)

    def add_to_rule_3(self, first_ent=None, connected=None, second_connector=None, first_connector=None):
        """
        The function creates the rule 3 relation
        :param prep_edge: edge to explore in the dependency graph
        :param connected_vertex: connected vertex represents the connected token on relation
        :param first_ent: the first entity
        :param first_connector: first connector between entities
        :param connected: the second entity
        :param second_connector: second connector between entities
        appends the extracted relation to self._rule_3_list
        """
        relation = Relation(first_ent,
                            connected,
                            second_connector,
                            first_connector=first_connector)

        if not self.find_relation(relation):
            self.add_to_relation_graph(first_ent=first_ent,
                                       connected_vertex=second_connector,
                                       connected=connected,
                                       first_connector=first_connector)
            # print("************** Rule 3 ACTIVATED **************")
            # print(relation)
            self._rule_3_list.append(relation)
            self.relation_list.append(relation)

    def find_relation(self, second_relation):
        """
        The function finds if the received relation is already mapped
        :param second_relation:
        :return: Boolean: True if relation was mapped, False otherwise.
        """
        for relation in self.relation_list:
            if relation.connection_backwards(second_relation):
                return True
        return False

    def Rule4(self):
        """
        The function activates Rule 4
        1. xcomp (X,Y) + dobj (Y,Z)
        appends the extracted relation to self._rule_4_list
        """
        for vertex in self.dep_graph:
            prep_edge = vertex.get_edge_by_dep("xcomp")
            for first_edge in prep_edge:
                connected_vertex = first_edge.target
                scnd_edge = connected_vertex.get_edge_by_dep("dobj")
                if is_verb(connected_vertex.token) or is_adp(connected_vertex.token):
                    for second_edge in scnd_edge:
                        if second_edge.target.token.text in self.entity_dict.keys():
                            connected = get_token_from_span(self.entity_dict[second_edge.target.token.text],
                                                            second_edge.target.token)
                        else:
                            connected = second_edge.target.token
                        if vertex.token.text in self.entity_dict.keys():
                            connected2 = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
                        else:
                            connected2 = vertex.token
                        relation = Relation(connected_vertex.token,
                                            connected,
                                            connected2)
                        self._rule_4_list.append(relation)
                        self.relation_list.append(relation)
                        self.add_to_relation_graph(first_ent=connected_vertex.token,
                                                   connected_vertex=connected,
                                                   connected=connected2)
                        # print("************** Rule 4 ACTIVATED **************")
                        # print(relation)

    def Rule_5(self):
        """
        Rule 5 tries to map between adp or PART instead of verb
        The function activates rule 5
        1. dobj (X, Y) + prep (T, X) + pobj (Z, T)
        appends the extracted relation to self._rule_5_list
        """
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                frst_edge = vertex.get_edge_by_dep("dobj")
                for first_edge in frst_edge:
                    connected_vertex = first_edge.target
                    scnd_edge = vertex.get_edge_by_dep("prep")
                    first_connector = connected_vertex.token
                    if is_verb(connected_vertex.token) or is_adp(connected_vertex.token):

                        for second_edge in scnd_edge:
                            connected_vertex = second_edge.target
                            prep_edge = connected_vertex.get_edge_by_dep("pobj")
                            second_connector = connected_vertex.token

                            # if is_verb(connected_vertex.token) or is_adp(connected_vertex.token) or is_part(
                            # TODO: test verb removed from if
                            if is_adp(connected_vertex.token) or is_part(connected_vertex.token):

                                for third_edge in prep_edge:
                                    if third_edge.target.token.text in self.entity_dict.keys():
                                        connected = get_token_from_span(self.entity_dict[third_edge.target.token.text],
                                                                        third_edge.target.token)
                                    else:
                                        connected = third_edge.target.token
                                    first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
                                    relation = Relation(first_ent,
                                                        connected,
                                                        second_connector,
                                                        first_connector=first_connector)
                                    if not self.find_relation(relation):
                                        # print("************** Rule 5 ACTIVATED **************")
                                        # print(relation)
                                        self._rule_5_list.append(relation)
                                        self.relation_list.append(relation)
                                        self.add_to_relation_graph(first_ent=first_ent,
                                                                   connected_vertex=second_connector,
                                                                   connected=connected,
                                                                   first_connector=first_connector)

    # def Rule_6(self, dependency):
    #     for vertex in self.dep_graph:
    #         if is_adp(vertex.token):
    #             prep_edge = vertex.get_edge_by_dep(dependency)
    #             for first_edge in prep_edge:
    #                 connected_vertex = first_edge.target
    #                 # first_entity = prep_edge.target.token
    #                 first_entity = self.get_current_connected(first_edge)
    #                 prep_edge = vertex.get_edge_by_dep("pobj")
    #                 # if prep_edge is not None and connected_vertex.token.text in self.entity_dict:
    #                 for second_edge in prep_edge:
    #                     connected = self.get_current_connected(second_edge)
    #                     # first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
    #                     # relation = Relation(token=first_entity,
    #                     #                     second_connector=vertex.token,
    #                     #                     connected_token=connected)
    #                     relation = Relation(token=connected,
    #                                         first_connector=first_entity,
    #                                         second_connector=vertex.token)
    #
    #                     self.relation_list.append(relation)
    #                     self._rule_5_list.append(relation)
    #                     print("************** Rule 6 ACTIVATED **************")
    #                     print(relation)

    def Rule_6(self):
        """
        Rule 6 handles and connections
        The function activated rule 6
        1. cc (X, Y) + conj (Y, Z)
        appends the extracted relation to self._rule_6_list
        """
        for vertex in self.dep_graph:
            if is_verb(vertex.token):
                first_edge = vertex.get_edge_by_dep("cc")
                for edge in first_edge:
                    connected_vertex = edge.target
                    second_edge = vertex.get_edge_by_dep("conj")
                    for curr_edge in second_edge:
                        if is_conj(connected_vertex.token):
                            connected = self.get_current_connected(curr_edge)
                            first_ent = self.entity_dict.get(vertex.token.text, vertex.token)
                            relation = Relation(first_connector=first_ent,
                                                second_connector=connected,
                                                token=connected_vertex.token)
                            self.relation_list.append(relation)
                            self.add_to_relation_graph(first_ent=first_ent,
                                                       connected_vertex=connected_vertex.token,
                                                       connected=connected)

                            self._rule_6_list.append(relation)
                            print("************** Rule 6 ACTIVATED **************")
                            print(relation)

    def Rule_7(self):
        """

        :return:
        """
        for vertex in self.dep_graph:
            if vertex.token in self.entity_dict:
                first_edge = vertex.get_edge_by_dep("nsubj")
                for edge in first_edge:
                    connected_vertex = edge.target
                    second_edge = vertex.get_edge_by_dep("prep")
                    for curr_edge in second_edge:
                        if is_conj(connected_vertex.token):
                            connected = self.get_current_connected(curr_edge)
                            first_ent = self.entity_dict.get(vertex.token.text, vertex.token)
                            relation = Relation(first_connector=first_ent,
                                                second_connector=connected,
                                                token=connected_vertex.token)
                            self.relation_list.append(relation)
                            self.add_to_relation_graph(first_ent=first_ent,
                                                       connected_vertex=connected_vertex.token,
                                                       connected=connected)

                            self._rule_6_list.append(relation)
                            print("************** Rule 6 ACTIVATED **************")
                            print(relation)

    def Rule_small(self):
        """
        The function handles small rules who didn't get any relation before
        1. dobj (X, Y)
        """
        if not self.find_no_extracted_relation():  # test if no relation has been extracted
            return
        for vertex in self.dep_graph:
            if vertex.token.text in self.entity_dict:
                edge_list = vertex.get_edge_by_dep("dobj")
                for edge in edge_list:
                    connected_vertex = edge.target
                    if not is_verb(connected_vertex.token):
                        continue
                    first_ent = get_token_from_span(self.entity_dict[vertex.token.text], vertex.token)
                    relation = Relation(token=first_ent, first_connector=connected_vertex.token)
                    self._small_rule_list.append(relation)
                    self.relation_list.append(relation)
                    self.add_to_relation_graph(first_ent=first_ent,
                                               first_connector=connected_vertex.token)

    def find_no_extracted_relation(self):
        """
        The function find if no relation was extracted
        :return: Boolean True if no rule was extracted, False otherwise
        """
        return not self._rule_1_list and not self._rule_2_list and not self._rule_3_list \
               and not self._rule_4_list and not self._rule_5_list

    def get_current_token(self, comp_list, vertex_token):
        """
        The function tries to find the right token in a list of tokens
        :param comp_list:
        :param vertex_token:
        :return: token from a list
        """
        for comp in comp_list:
            if self._doc[vertex_token.i:vertex_token.i + 1] == comp:
                return comp

    def get_span(self, entity, comp=None, vertex_token=None):
        """
        The function returns a span from received tokens
        :param vertex_token:
        :param entity:
        :param comp:
        :return: Span, representing two tokens
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

    def add_to_relation_graph(self, first_ent, connected_vertex=None, connected=None, **kwargs):
        """
        The functions adds a relation to the relations graph
        :param first_ent:
        :param connected_vertex:
        :param connected:
        :param kwargs:
        :return:
        """
        first_ent_vertex = self.relation_graph.get_vertex(first_ent)
        if not first_ent_vertex:
            first_ent_vertex = RelationVertex(first_ent)
            self.relation_graph.insert(first_ent_vertex)
        if kwargs.get("first_connector"):
            first_connector_vertex = self.relation_graph.get_vertex(kwargs.get("first_connector"))
            if not first_connector_vertex:
                first_connector_vertex = RelationVertex(kwargs.get("first_connector"))
                self.relation_graph.insert(first_connector_vertex)
            edge = RelationEdge(first_connector_vertex, first_ent_vertex)
        if connected_vertex and connected:
            second_ent_vertex = self.relation_graph.get_vertex(connected_vertex)
            if not second_ent_vertex:
                second_ent_vertex = RelationVertex(connected_vertex)
                self.relation_graph.insert(second_ent_vertex)
            edge = RelationEdge(first_ent_vertex, second_ent_vertex)
            third_end_vertex = self.relation_graph.get_vertex(connected)
            if not third_end_vertex:
                third_end_vertex = RelationVertex(connected)
                self.relation_graph.insert(third_end_vertex)
            edge = RelationEdge(second_ent_vertex, third_end_vertex)

    def get_current_connected(self, prep_edge):
        """
        The functions tries to find an edge target in entity dict
        :param prep_edge:
        :return: token from entity dict if edge target exists there
        """
        if prep_edge.target.token.text in self.entity_dict.keys():
            return get_token_from_span(self.entity_dict[prep_edge.target.token.text],
                                       prep_edge.target.token)
        else:
            return prep_edge.target.token
