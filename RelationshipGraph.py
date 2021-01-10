class RelationVertex(object):

    def __init__(self, token, **kwargs):
        self.token = token
        self.edge_list = []
        # self.attributes = []

    def __repr__(self):
        return "TOKEN: " + str(self.token) + " EDGES: " + str(self.edge_list)

    def __eq__(self, other):
        return isinstance(self.token, type(other.token)) and self.token == other.token

    def add_edge(self, edge):
        if edge not in self.edge_list:
            self.edge_list.append(edge)


class RelationEdge(object):

    def __init__(self, vertex, second_vertex):
        self.first_target = vertex
        # self.dependency = dependency
        self.second_target = second_vertex
        self.first_target.add_edge(self)
        # self.second_target.add_edge(self)

    def __repr__(self):
        return str(self.second_target)

    def __eq__(self, other):
        return self.first_target == other.first_target and self.second_target == other.second_target
