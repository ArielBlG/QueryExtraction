class Node(object):

    def __init__(self, dep, **kwargs):
        self.dep = dep
        if "first_word" in kwargs:
            self.first_word = kwargs["first_word"]
        if "second_word" in kwargs:
            self.second_word = kwargs["second_word"]

    def __repr__(self):
        return "Dependency:" + str(self.dep) + \
               ", First Word:" + self.first_word.text + ", Second Word:" + self.second_word.text

    def __iter__(self):
        pass

    def __eq__(self, other):
        return (self.dep == other.dep) and (self.first_word == other.first_word) and \
               (self.second_word == other.second_word)


class Vertex(object):

    def __init__(self, token, **kwargs):
        self.token = token
        self.edge_list = []
        self.attributes = []

    def __repr__(self):
        return str(self.token)

    def __eq__(self, other):
        return self.token == other.token

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def get_edge_by_dep(self, dep):
        edge_list = []
        for edge in self.edge_list:
            if edge.dependency == dep:
                edge_list.append(edge)
        return edge_list

    def get_edge_by_dep_iter(self, dep):
        for edge in self.edge_list:
            if edge.dependency == dep:
                yield edge


class Edge(object):

    def __init__(self, vertex, dependency):
        self.target = vertex
        self.dependency = dependency

    def __repr__(self):
        return "---" + self.dependency + "-->" + self.target.token.text


class Graph:

    def __init__(self):
        self.nodes = []
        self.vertexs = []
        self.edges = []

    def insert(self, vertex):
        self.vertexs.append(vertex)

    def get_vertex(self, vertex):
        for v in self.vertexs:
            if v.token == vertex:
                return v
        return None

    def new_edge(self, first_vertex, second_vertex, dependency):
        first_vertex.add_edge(Edge(second_vertex, dependency))
        second_vertex.add_edge(Edge(first_vertex, dependency))

    def insert_nodes(self, node):
        self.nodes.append(node)

    def getNodesBySource(self, source):
        return self.nodes_by_source[str(source)]

    def getNodesByTarget(self):
        pass

    def __iter__(self):
        yield from self.vertexs

    def __next__(self):
        pass

