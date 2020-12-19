import DepGraph

rule_3_list = ["enter", "input", "save", "adds", "has"]


class EntAtRules:

    def __init__(self):

        self.entities = []
        self.attributes = []
        self.depend_graph = None

    # def initialize(self, dep_graph, tokens_list):
    #     depend_graph = DepGraph.Graph()
    #     dep_length = len(dep_graph.edge)
    #     for index in range(0, dep_length):
    #         temp_node = DepGraph.Node(dep_graph.edge[index].dep, dep_graph.edge[index].source,
    #                                   dep_graph.edge[index].target, index)
    #         depend_graph.insert_nodes(temp_node)
    #         # if index == 0:
    #         #     self.Rules_Classifier(dep_graph.edge[0], tokens_list)
    #         # else:
    #         #     self.Rules_Classifier(dep_graph.edge[index], tokens_list, prev_dep=dep_graph.edge[index-1])
    #     for node in depend_graph:
    #         if str(node.target) in depend_graph.nodes_by_source.keys():
    #             node.previous = depend_graph.nodes_by_source[str(node.target)]
    #         if str(node.target) in depend_graph.nodes_comp_source.keys():
    #             node.previous_compound.append(depend_graph.nodes_comp_source[str(node.target)])
    #     for node in depend_graph:
    #         self.Rules_Classifier(node.dep, tokens_list, node.source, node.target, node.previous_compound,
    #                               node.previous)
    #     print(self.entities)
    #     print(self.attributes)

    def Rules_Classifier(self, dependency, tokens_list, source, target, prev_comp, prev_dep, **kwargs):
        if "node" in kwargs:
            node = kwargs["node"]
        if "depend_graph" in kwargs:
            self.depend_graph = kwargs.get("depend_graph")
        A = source - 1
        B = target - 1
        if dependency == "nsubj" or dependency == "nsubj:pass" or dependency == "nsubj:xsubj":
            self.Rule_1_2(A, B, tokens_list, prev_comp, node=node)
        if dependency == "obj":
            self.Rule_3_4_5(A, B, tokens_list, prev_dep, prev_comp, node=node)
        if dependency == "nmod:of":
            self.Rule_6(A, B, tokens_list, node=node)
        if dependency == "nmod:in":
            self.Rule_7(A, B, tokens_list, node=node)
        if dependency == "obl:to" or dependency == "obl:for" or dependency == "obl:from" or dependency == "obl:as":
            self.Rule_8(A, B, tokens_list, node=node)
        if dependency == "obl:by" or dependency == "obl:agent" or dependency == "obl:with":
            self.Rule_9(A, B, tokens_list, node=node)
        if dependency == "nmod:poss":
            self.Rule_10(A, B, tokens_list, node=node)
        if dependency == "amod":
            self.Rule_11(A, B, tokens_list, node=node)
        if dependency == "compound":
            self.Rule_12(A, B, tokens_list, node=node)
        if dependency == "obl:and" or dependency == "obl:or":
            self.Rule_13(A, B, tokens_list, node=node)
        return self.depend_graph

    def comp_finder(self, prev_comp, tokens_list, self_list, ent=False, node=None):
        for prev in prev_comp:
            if prev.dep == "compound":
                A_comp = prev.source - 1
                B_comp = prev.target - 1
                self_list.append(tokens_list[B_comp].lemma + ' ' + tokens_list[A_comp].lemma)
                if ent:
                    self.depend_graph.remove(prev) # TODO: fix delete
                    new_word = tokens_list[B_comp].word + ' ' + tokens_list[A_comp].word
                    new_lemma = tokens_list[B_comp].lemma + ' ' + tokens_list[A_comp].lemma
                    tokens_list[B_comp].word = new_word
                    tokens_list[A_comp].word = new_word
                    tokens_list[A_comp].lemma = new_lemma
                    tokens_list[B_comp].lemma = new_lemma

                return True

        return False

    def Rule_1_2(self, A, B, tokens_list, prev_dep, **kwargs):
        node = None
        if "node" in kwargs:
            node = kwargs["node"]
        pos = tokens_list[A].pos
        pos2 = tokens_list[B].pos
        if (tokens_list[A].pos.startswith("VB") or tokens_list[A].pos.startswith("NN")) and tokens_list[
            B].pos.startswith("NN"):
            if tokens_list[B].lemma in self.attributes:
                self.Rule_2()
            else:
                self.Rule_1(A, B, tokens_list, prev_dep, node=node)
            # elif prev_dep is not None:
            #     if prev_dep != "amod" and prev_dep != "advmod" and tokens_list[A].word not in rule_3_list:
            #         self.Rule_3()
            #     else:
            #         self.Rule_1()

    def Rule_1(self, A, B, tokens_list, prev_dep, **kwargs):
        node = None
        if "node" in kwargs:
            node = kwargs["node"]
        if not self.comp_finder(prev_dep, tokens_list, self.entities, True, node):
            self.entities.append(tokens_list[B].word)

    def Rule_2(self, A, B, tokens_list, prev_dep, **kwargs):
        if not self.comp_finder(prev_dep, tokens_list, self.attributes):
            self.attributes.append(tokens_list[B].word.lemma)

    def Rule_3_4_5(self, A, B, tokens_list, prev_dep, prev_comp, **kwargs):
        node = None
        if "node" in kwargs:
            node = kwargs["node"]
        # TODO: split to 3, 4, 5 functions
        if (tokens_list[A].pos.startswith("VB")) and (tokens_list[B].pos.startswith("NN")):
            for prev in prev_dep:
                if tokens_list[B].lemma not in self.attributes and prev.dep != "amod" and prev.dep != "advmod" and \
                        tokens_list[A].lemma not in rule_3_list:
                    self.Rule_3(A, B, tokens_list, prev_dep, node=node)
                elif tokens_list[B].lemma in self.attributes or tokens_list[A].lemma in rule_3_list:
                    self.Rule_4_5(A, B, tokens_list, prev_comp, prev_dep)
            if prev_dep is not []:
                if tokens_list[B].lemma not in self.attributes and tokens_list[A].lemma not in rule_3_list:
                    self.Rule_3(A, B, tokens_list, prev_dep, node=node)
                elif tokens_list[B].lemma in self.attributes or tokens_list[A].lemma in rule_3_list:
                    self.Rule_4_5(A, B, tokens_list, prev_comp, prev_dep)

    def Rule_3(self, A, B, tokens_list, prev_comp, **kwargs):
        node = None
        if "node" in kwargs:
            node = kwargs["node"]
        if not self.comp_finder(prev_comp, tokens_list, self.entities, True, node):
            self.entities.append(tokens_list[B].word)

    def Rule_4_5(self, A, B, tokens_list, prev_comp, prev_dep, **kwargs):
        for prev in prev_dep:
            if (prev.dep == "amod" or prev.dep == "advmod") and tokens_list[prev.target - 1].pos == "JJ":
                self.attributes.append(tokens_list[prev.target - 1].lemma + tokens_list[prev.source - 1].lemma)
            else:
                # TODO: fix rule 4
                self.Rule_4(A, B, tokens_list, prev_comp, prev_dep)

    def Rule_4(self, A, B, tokens_list, prev_comp, prev_dep, **kwargs):
        if not self.comp_finder(prev_comp, tokens_list, self.attributes):
            self.attributes.append(tokens_list[B].lemma)

    def Rule_5(self, **kwargs):
        pass

    def Rule_6(self, A, B, tokens_list, **kwargs):
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma in self.attributes) and (tokens_list[B].lemma not in self.attributes):
            self.entities.append(tokens_list[B].word)
            self.attributes.append(tokens_list[A].lemma)
        elif (tokens_list[A].lemma not in self.attributes) and (tokens_list[B].lemma not in self.attributes):
            self.entities.append(tokens_list[B].word)
            self.entities.append(tokens_list[A].word)
        elif (tokens_list[A].lemma in self.attributes) and (tokens_list[B].lemma in self.attributes):
            self.attributes.append(tokens_list[A].lemma + "of" + tokens_list[B].lemma)

    def Rule_7(self, A, B, tokens_list, **kwargs):
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")):
            self.entities.append(tokens_list[B].word)
            self.attributes.append(tokens_list[A].lemma)

    def Rule_8(self, A, B, tokens_list, **kwargs):
        if tokens_list[B].pos.startswith("NN"):
            self.entities.append(tokens_list[B].word)

    def Rule_9(self, A, B, tokens_list, **kwargs):
        if tokens_list[B].pos.startswith("NN") and tokens_list[B].lemma in self.attributes:
            # TODO: delete
            self.attributes.append(tokens_list[B].lemma)
        elif tokens_list[B].pos.startswith("NN") and tokens_list[B].lemma not in self.attributes:
            self.entities.append(tokens_list[B].word)

    def Rule_10(self, A, B, tokens_list, **kwargs):
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")):
            self.entities.append(tokens_list[B].word)
            self.attributes.append(tokens_list[A].lemma)
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("PRP")) and (
                tokens_list[B].lemma not in self.attributes):
            self.attributes.append(tokens_list[A].lemma)

    def Rule_11(self, A, B, tokens_list, **kwargs):
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos == "JJ") and (
                tokens_list[A].lemma in self.attributes):
            self.attributes.append(tokens_list[B].lemma + tokens_list[A].word.lemma)
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos == "JJ") and (
                tokens_list[A].lemma not in self.attributes):
            self.entities.append(tokens_list[A].word)

    def Rule_12(self, A, B, tokens_list, **kwargs):
        if "node" in kwargs:
            node = kwargs["node"]
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma in self.attributes) and (tokens_list[B].lemma not in self.attributes):
            self.attributes.append(tokens_list[B].lemma + tokens_list[A].lemma)
            self.entities.append(tokens_list[B].word)
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma not in self.attributes) and (tokens_list[B].lemma in self.attributes):
            self.attributes.append(tokens_list[A].lemma + tokens_list[B].lemma)
            self.entities.append(tokens_list[A].word)
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma not in self.attributes) and (
                tokens_list[B].lemma not in self.attributes):
            self.entities.append(tokens_list[B].word + ' ' + tokens_list[A].word)
            self.depend_graph.remove(node)
            tokens_list[A].word = tokens_list[B].word + ' ' + tokens_list[A].word
            tokens_list[A].lemma = tokens_list[B].lemma + ' ' + tokens_list[A].lemma
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma in self.attributes) and (tokens_list[B].lemma in self.attributes):
            self.attributes.append(tokens_list[B].lemma + tokens_list[A].lemma)

    def Rule_13(self, A, B, tokens_list, **kwargs):
        if (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma in self.attributes) and (tokens_list[B].lemma in self.attributes):
            self.attributes.append(tokens_list[A].lemma)
            self.attributes.append(tokens_list[B].lemma)
        elif (tokens_list[A].pos.startswith("NN")) and (tokens_list[B].pos.startswith("NN")) and (
                tokens_list[A].lemma not in self.attributes) and (
                tokens_list[B].lemma not in self.attributes):
            self.entities.append(tokens_list[A].word)
            self.entities.append(tokens_list[B].word)


class Relation(object):

    def __init__(self, first_object, connector, second_object):
        self.left = first_object
        self.right = second_object
        self.connector = connector

    def __repr__(self):
        return self.left + ' (' + self.connector + ') ' + self.right


class RelationExtract:

    def __init__(self):
        self.entities = []
        self.relationship = []
        self.depend_graph = None

    def Rules_Classifier(self, dependency, tokens_list, source, target):
        src = source - 1
        tgt = target - 1
        if dependency == "nsubj":
            self.Rules_14_17_18_20_21_22(src, tgt, tokens_list)
        if dependency == "nsubj:pass":
            self.Rules_15_19(src, tgt, tokens_list)
        if dependency == "nmod:of":
            self.Rule_16(src, tgt, tokens_list)
        if dependency == "obl:as":
            self.Rule_23(src, tgt, tokens_list)
        if dependency == "nsubj:xsubj":
            self.Rule_temp(src, tgt, tokens_list)

    def Rules_14_17_18_20_21_22(self, src, tgt, tokens_list):
        nodes_source = self.depend_graph.getNodesBySource(src + 1)

        for node in nodes_source:
            if node.dep == "obj":
                self.Rules_14_17_18(src, tgt, tokens_list, node, nodes_source)
            if node.dep == "nsubj:pass":
                for scnd_node in nodes_source:
                    if scnd_node.dep == "obl:to":
                        self.Rule_18_20(src, tgt, tokens_list, scnd_node, node)
            if node.dep == "nmod:in":
                self.Rule_21_22(src, tgt, tokens_list, node, "in")
            if node.dep == "obl:for":
                self.Rule_21_22(src, tgt, tokens_list, node, "for")

    def Rules_14_17_18(self, src, tgt, tokens_list, scnd_node, node_source):
        for node in node_source:
            if node.dep == "nmod:of":
                self.Rule_17(src, tgt, tokens_list, scnd_node, node)
                return
            if node.dep == "obl:to":
                self.Rule_18_20(src, tgt, tokens_list, scnd_node, node)
                return

        self.Rule_14(src, tgt, tokens_list, scnd_node)

    def Rule_17(self, src, tgt, tokens_list, scnd_node, thrd_node):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word,
                                              tokens_list[scnd_node.target - 1].word))

        if tokens_list[thrd_node.source - 1].word in self.entities and \
                tokens_list[thrd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[thrd_node.target - 1].word, "has",
                                              tokens_list[thrd_node.source - 1].word))

    def Rule_18_20(self, src, tgt, tokens_list, scnd_node, thrd_node):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word,
                                              tokens_list[scnd_node.target - 1].word))

        if tokens_list[scnd_node.target - 1].word in self.entities and \
                tokens_list[thrd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[scnd_node.target - 1].word, tokens_list[src].word + " to",
                                              tokens_list[thrd_node.target - 1].word))

        if tokens_list[tgt].word in self.entities and tokens_list[thrd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word + " to",
                                              tokens_list[thrd_node.target - 1].word))

    def Rule_21_22(self, src, tgt, tokens_list, scnd_node, word):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word + word,
                                              tokens_list[scnd_node.target - 1].word))

    def Rule_14(self, src, tgt, tokens_list, scnd_node):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word,
                                              tokens_list[scnd_node.target - 1].word))

    def Rules_15_19(self, src, tgt, tokens_list):
        nodes_source = self.depend_graph.getNodesBySource(src + 1)

        for node in nodes_source:
            if node.dep == "obl:agent" or node.dep == "obl:by":
                self.Rule_15(src, tgt, tokens_list, node)
            if node.dep == "obl:to":
                self.Rule_19(src, tgt, tokens_list, node)

    def Rule_15(self, src, tgt, tokens_list, scnd_node):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word,
                                              tokens_list[scnd_node.target - 1].word))

    def Rule_19(self, src, tgt, tokens_list, scnd_node):
        if tokens_list[tgt].word in self.entities and tokens_list[scnd_node.target - 1].word in self.entities:
            self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word + " to",
                                              tokens_list[scnd_node.target - 1].word))

    def Rule_16(self, src, tgt, tokens_list):
        # TODO: Card of the customer has an expiry date
        if tokens_list[tgt].word in self.entities and tokens_list[src].word in self.entities:
            self.relationship.append(Relation(tokens_list[src].word, "of", tokens_list[tgt].word))

    def Rule_23(self, src, tgt, tokens_list):
        nodes_source = self.depend_graph.getNodesBySource(src + 1)
        for node in nodes_source:
            if node.dep == "obj":
                if tokens_list[tgt].word in self.entities and tokens_list[node.target - 1].word in self.entities:
                    self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word,
                                                      tokens_list[node.target - 1].word))

    def Rule_temp(self, src, tgt, tokens_list):
        nodes_source = self.depend_graph.getNodesBySource(src + 1)

        for node in nodes_source:
            if node.dep == "obj":
                self.relationship.append(Relation(tokens_list[tgt].word, tokens_list[src].word ,
                                                  tokens_list[node.target - 1].word))
