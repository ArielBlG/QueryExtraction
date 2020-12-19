class EntAtExtractor(object):

    def __init__(self, graph, **kwargs):
        self.graph = graph
        self.entities = []
        self.attributes = []

    def extract_att_from_ents(self):
        for node in self.graph:
            if node.first_is_entity and node.second_is_entity:
                if node.dep == "compund":
                    self.attributes.append(node.target)
                    self.entities.append(node.source)
            else:
                self.entities.append(node.source)
                self.entities.append(node.target)
