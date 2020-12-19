# import stanfordnlp
# from stanfordnlp.server import CoreNLPClient
import NLPRules
import RulesInitizalizer
import spacy
# from spacy.pipeline import EntityRuler
from SpacyExtenstions import EntityMatcher
import newDepGraph
import EntityExtractor
import AttributeExtractor
import pandas as pd
import PreProcessText
import RelationshipExtractor
from TextQueries import *
import csv
nlp = spacy.load('en_core_web_sm')

# import neuralcoref

# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')


nlp_rules = NLPRules.EntAtRules()
problem_words = ["to", "end", "of", "in"]
init = RulesInitizalizer.Initialize()


def read_new_queries():
    path = "/Users/ariel-pc/Desktop/new_queries.csv"
    data = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        read = list(reader)
        for row in read:
            try:
                data.append(row[0])
            except IndexError:
                break
    return data


def create_class_ents():
    path = """/Users/ariel-pc/Desktop/Work/Java8/JavaMethods.txt"""
    with open(path) as f:
        content = f.readlines()
    method_names = [x.strip() for x in content]
    name_dict = {"name": method_names}
    path = """/Users/ariel-pc/Desktop/Work/Java8/Java8Classes.txt"""
    with open(path) as f:
        content = f.readlines()
    class_names = [x.strip() for x in content]
    name_dict["name"] += class_names
    entity_matcher = EntityMatcher(nlp, method_names, "JavaMethods", class_names, "JavaClasses")
    nlp.add_pipe(entity_matcher, after="ner")

    return name_dict


# def extract_att_from_ents(graph):
#     attributes = []
#     entities = []
#     for node in graph:
#         if isinstance(node.first_word, TaskWrapper.EntityWrapper) and \
#                 isinstance(node.second_word, TaskWrapper.EntityWrapper):
#             if node.dep == "compound":
#                 # attributes.append(node.second_word.text)
#                 if node.first_word.text not in entities and node.first_word.text not in problem_words:
#                     # node.first_word.attributes.append(TaskWrapper.AttributeWrapper(node.second_word))
#                     node.first_word.text += " " + node.second_word.text
#                     # entities.append(node.first_word.text)
#
#             else:
#                 if node.first_word.text not in entities and node.first_word.text not in problem_words:
#                     entities.append(node.first_word.text)
#                 if node.second_word.text not in entities and node.second_word.text not in problem_words:
#                     entities.append(node.second_word.text)
#         elif isinstance(node.first_word, TaskWrapper.EntityWrapper) or \
#                 isinstance(node.second_word, TaskWrapper.EntityWrapper):
#             if isinstance(node.first_word, TaskWrapper.EntityWrapper):
#                 if node.first_word.text not in entities and node.first_word.text not in problem_words:
#                     entities.append(node.first_word.text)
#             if isinstance(node.second_word, TaskWrapper.EntityWrapper):
#                 if node.second_word.text not in entities and node.second_word.text not in problem_words:
#                     entities.append(node.second_word.text)
#     return entities


def Main():
    df_clean = create_class_ents()
    df = pd.DataFrame(columns=['Question', 'Relation'])
    index = -1
    rows_list = []
    entities_list = []
    new_queries = read_new_queries()
    for text in new_queries:
        # if text != "How to use interface to communicate between two activities":
        #     continue
        index = index + 1
        pre_process_init = PreProcessText.PreProcessText(text)
        text_after_preprocess = pre_process_init.preprocess_text(df_clean)
        print("########################################################")
        print(text_after_preprocess)
        doc = nlp(text_after_preprocess)
        entity_extractor = EntityExtractor.EntityExtractor(text, newDepGraph.Graph(), doc.ents, doc)
        entity_extractor.init_extraction()
        # print(entity_extractor.entity_after_filter)
        attribute_extractor = AttributeExtractor.AttributeExtractor(text,
                                                                    entity_extractor.dep_graph,
                                                                    entity_extractor.entity_after_filter,
                                                                    doc,
                                                                    entity_extractor.entity_dict)
        attribute_extractor.initiate_extractor()
        relationship_extractor = RelationshipExtractor.RelationshipExtractor(text,
                                                                             entity_extractor.dep_graph,
                                                                             entity_extractor.entity_after_filter,
                                                                             doc,
                                                                             attribute_extractor.entity_dict)
        relationship_extractor.init_extraction()

        # comp_nouns = (get_compound_nouns(text, doc))
        # print([(ent.text, ent.label_) for ent in doc.ents])
        # nouns = (get_nouns(doc))
        dict1 = {}
        dict1["Question"] = text
        dict1["Relation"] = relationship_extractor.entity_tasks
        #     dict1["Nouns"] = nouns
        #     dict1["Compound"] = comp_nouns
        rows_list.append(dict1)
    df = pd.DataFrame(rows_list)
    df.to_csv("relation.csv")
    # with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
    #                    timeout=50000, memory='16G') as client:
    #     ann = client.annotate(new_text)
    #     sents = ann.sentence
    #
    # for sent in sents:
    #     init.initialize(sent.enhancedPlusPlusDependencies, sent.token)


if __name__ == "__main__":
    Main()
