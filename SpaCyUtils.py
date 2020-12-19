from spacy.tokens.token import Token


def get_tokens(tree):
    return [t._text for t in tree]


def get_lower_tokens(tree):
    return [str.lower(t._text) for t in tree]


def get_head(tree):
    for t in tree:
        if t == t.head:
            return t


def get_idx(tree):
    return [t.i for t in tree]


def get_span(story, li, part='data'):
    ret = []
    for i in get_idx(li):
        ret.append(eval('story.' + str(part))[i])
    return ret


def _get(story, span, f_func):
    return get_span(story, list(filter(f_func, span)))


def is_noun(token):
    if token.pos_ == "NOUN" or token.pos_ == "PROPN":
        return True
    return False


def is_adp(token):
    return token.pos_ == "ADP"


def is_part(token):
    return token.pos_ == "PART"


def is_verb(token):
    if token.pos_ == "VERB":
        return True
    return False


def get_token_from_span(span_list: object, token: object) -> object:
    if isinstance(span_list, list):
        for span in span_list:
            for _token in span:
                if _token == token:
                    return span
    else:
        for _token in span_list:
            if _token == token:
                return span_list

    return token


def is_compound(token):
    if token.dep_ == "compound" \
            or (token.dep_ == "amod" and is_noun(token)) \
            or (token.dep_ == "appos" and is_noun(token)) \
            or (token.dep_ == "poss" and is_noun(token)):
        return True
    return False


def is_subject(token):
    if token.dep_[:5] == 'nsubj':
        return True
    return False


def is_dobj(token):
    if token.dep_ == 'dobj':
        return True
    return False


def get_nouns(story):
    return [noun for noun in story if is_noun(noun)]


def get_nouns_span(story):  # TODO: fix to one function
    return [story[noun.i: noun.i + 1] for noun in story if is_noun(noun)]


def get_compound_nouns(story, span):
    compounds = []
    # nouns = get_nouns(story, span)
    nouns = get_nouns(span)

    for token in nouns:
        for child in token.children:
            if is_compound(child):
                # Replace to take rightmost child
                if child.idx < token.idx:
                    for compound in compounds:
                        if child in compound or token in compound:
                            compounds.remove(compound)
                compounds.append([child, token])

    if compounds and len(compounds) == 0 and type(compounds[0]) is list:
        compounds = compounds[0]

    return compounds


