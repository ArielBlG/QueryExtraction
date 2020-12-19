import DepGraph
import NLPRules

nlp_rules = NLPRules.EntAtRules()
relation_rules = NLPRules.RelationExtract()


class Initialize:

    def __init__(self):
        self.depend_graph = DepGraph.Graph()
        self.attributes = set()
        self.entities = set()
        self.relationship = []

    def initialize(self, dep_graph, tokens_list):
        self.depend_graph = DepGraph.Graph()
        dep_length = len(dep_graph.edge)
        for index in range(0, dep_length):
            temp_node = DepGraph.Node(dep_graph.edge[index].dep, dep_graph.edge[index].source,
                                      dep_graph.edge[index].target, index)
            self.depend_graph.insert_nodes(temp_node)

        for node in self.depend_graph:
            if str(node.target) in self.depend_graph.nodes_by_source.keys():
                node.previous = self.depend_graph.nodes_by_source[str(node.target)]
            if str(node.target) in self.depend_graph.nodes_comp_source.keys():
                node.previous_compound.append(self.depend_graph.nodes_comp_source[str(node.target)])

        """add entities and attributes"""
        # nlp_rules.depend_graph = self.depend_graph
        for node in self.depend_graph:
            new_graph = nlp_rules.Rules_Classifier(node.dep, tokens_list, node.source, node.target, node.previous_compound,
                                       node.previous, node=node, depend_graph=self.depend_graph)

            self.entities = nlp_rules.entities
            self.attributes = nlp_rules.attributes
        self.depend_graph = new_graph

        print(self.entities)
        print(self.attributes)

        relation_rules.depend_graph = self.depend_graph
        relation_rules.entities = self.entities
        """add relationships"""
        for node in self.depend_graph:
            relation_rules.Rules_Classifier(node.dep, tokens_list, node.source, node.target)
            self.relationship = relation_rules.relationship
        print(self.relationship)
