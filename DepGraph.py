"""edge {
  source: 2
  target: 1
  dep: "compound"
  isExtra: false
  sourceCopy: 0
  targetCopy: 0
  language: UniversalEnglish
}"""


class Node(object):

    def __init__(self, dep, source, target, idx, **kwargs):
        self.dep = dep
        self.source = source
        self.target = target
        self.index = idx
        self.previous = []
        self.previous_compound = []
        self.first_is_entity = False
        self.second_is_entity = False
        if "first_word" in kwargs:
            self.first_word = kwargs["first_word"]
        if "second_word" in kwargs:
            self.second_word = kwargs["second_word"]

    def __repr__(self):
        return "Dependency:" + str(self.dep) + ", First Word:" + self.first_word + ", Second Word:" + self.second_word

    def __iter__(self):
        pass

    def __eq__(self, other):
        return (self.dep == other.dep) and (self.source == other.source) and (self.target == other.target)


class Graph:

    def __init__(self):
        self.nodes = []
        self.nodes_by_source = {}
        self.nodes_by_target = {}
        self.nodes_comp_source = {}
        self.nodes_comp_target = {}

        self.nodes_comp_source_temp = {}
        self.nodes_comp_target_temp = {}

    def insert(self, node):
        self.nodes.append(node)

    def insert_nodes(self, node):
        self.nodes.append(node)
        if str(node.source) not in self.nodes_by_source:
            self.nodes_by_source[str(node.source)] = []
        self.nodes_by_source[str(node.source)].append(node)
        if str(node.target) not in self.nodes_by_target:
            self.nodes_by_target[str(node.target)] = []
        self.nodes_by_target[str(node.target)].append(node)

        if node.dep == "compound":
            # TODO: check if list
            self.nodes_comp_source[str(node.source)] = node
            self.nodes_comp_target[str(node.target)] = node

    def getNodesBySource(self, source):
        return self.nodes_by_source[str(source)]

    def getNodesByTarget(self):
        pass

    def __iter__(self):
        yield from self.nodes

    def __next__(self):
        pass

    def remove(self, instance):
        if instance in self.nodes_by_source[str(instance.source)]:
            self.nodes_by_source[str(instance.source)].remove(instance)
        if instance in self.nodes_by_target[str(instance.target)]:
            self.nodes_by_target[str(instance.target)].remove(instance)
        if instance.dep == "compound":
            if str(instance.source) in self.nodes_comp_source.keys():
                del self.nodes_comp_source[str(instance.source)]
            if str(instance.source) in self.nodes_comp_target.keys():
                del self.nodes_comp_target[str(instance.target)]
        for node in self.nodes:
            if instance in node.previous:
                node.previous.remove(instance)
            if instance in node.previous_compound:
                node.previous_compound.remove(instance)
        if instance in self.nodes:
            self.nodes.remove(instance)
