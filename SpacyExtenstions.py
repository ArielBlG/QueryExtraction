from spacy.matcher import PhraseMatcher
from spacy.tokens import Span


class EntityMatcher(object):
    name = "entity_matcher"

    def __init__(self, nlp, terms, label, scnd_term, scnd_label):
        patterns = [nlp.make_doc(text) for text in terms]
        scnd_patterns = [nlp.make_doc(text) for text in scnd_term]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)
        self.matcher.add(scnd_label, None, *scnd_patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        seen_tokens = set()
        new_entities = []
        entities = doc.ents
        for match_id, start, end in matches:
            # check for end - 1 here because boundaries are inclusive
            if start not in seen_tokens and end - 1 not in seen_tokens:
                new_entities.append(Span(doc, start, end, label=match_id))
                entities = [
                    e for e in entities if not (e.start < end and e.end > start)
                ]
                seen_tokens.update(range(start, end))

        doc.ents = tuple(entities) + tuple(new_entities)
        return doc
