from sklearn.feature_extraction.text import TfidfVectorizer
from sparse_dot_topn import awesome_cossim_topn
import re
import numpy as np
import pandas as pd


def get_matches_df(sparse_matrix, A, B, top=100):
    non_zeros = sparse_matrix.nonzero()

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = A[sparserows[index]]
        right_side[index] = B[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]

    return pd.DataFrame({'wrong_word': left_side,
                         'right_word': right_side,
                         'similarity': similairity})


def ngrams(string, n=3):
    string = (re.sub(r'[,-./]|\sBD', r'', string)).upper()
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


class PreProcessText:

    def __init__(self, text):
        self.text_to_preprocess = text

    def self_written_preprocess_rules(self):
        """handle list typo"""
        if "ist" in self.text_to_preprocess:
            if "inke" in self.text_to_preprocess:  # handle linked list typo
                if "linked List" in self.text_to_preprocess:
                    self.text_to_preprocess = self.text_to_preprocess.replace("linked List", "LinkedList")
                if "linked lists" in self.text_to_preprocess:
                    self.text_to_preprocess = self.text_to_preprocess.replace("linked lists", "LinkedList")
            elif "ray" in self.text_to_preprocess:  # handle array list typo
                if "Array List" in self.text_to_preprocess:
                    self.text_to_preprocess = self.text_to_preprocess.replace("Array List", "ArrayList")

            """handle tree type"""
        elif "ree" in self.text_to_preprocess:
            if "binary tree" in self.text_to_preprocess:
                self.text_to_preprocess = self.text_to_preprocess.replace("binary tree", "BinaryTree")
            if "Binary Tree" in self.text_to_preprocess:
                text_to_preprocess = self.text_to_preprocess.replace("Binary Tree", "BinaryTree")

        return self.text_to_preprocess

    def preprocess_text(self, df_clean):
        self.text_to_preprocess = self.remove_unneeded_text()
        df_dirty = {"name": self.text_to_preprocess.split()}

        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
        tf_idf_matrix_clean = vectorizer.fit_transform(df_clean['name'])
        tf_idf_matrix_dirty = vectorizer.transform(df_dirty['name'])

        matches = awesome_cossim_topn(tf_idf_matrix_dirty, tf_idf_matrix_clean.transpose(), 1, 0)

        matches_df = get_matches_df(matches, df_dirty['name'], df_clean['name'], top=0)
        matches_df = matches_df.loc[matches_df['similarity'] >= 0.85]
        for index, row in matches_df.iterrows():
            if row["wrong_word"] != row["right_word"]:
                if "get" in row["right_word"]:
                    if row["similarity"] > 0.95:
                        self.text_to_preprocess = self.text_to_preprocess.replace(row["wrong_word"], row["right_word"])
                else:
                    self.text_to_preprocess = self.text_to_preprocess.replace(row["wrong_word"], row["right_word"])

        return self.self_written_preprocess_rules()

    def remove_unneeded_text(self):
        self.text_to_preprocess = self.text_to_preprocess.replace("java.util", "")
        text = self.text_to_preprocess .split(' ', 1)
        if text[0].lower() == 'java':
            self.text_to_preprocess = text[1]
        else:
            self.text_to_preprocess = text[0] + ' ' + text[1]
        text = self.text_to_preprocess .split(' ', 2)
        how_to_text = text[0].lower() + ' ' + text[1].lower()
        if how_to_text == 'how to':
            self.text_to_preprocess = text[2]
        else:
            self.text_to_preprocess = text[0] + ' ' + text[1] + ' ' + text[2]
        # self.text_to_preprocess = self.text_to_preprocess.replace("java", "")
        # self.text_to_preprocess = self.text_to_preprocess.replace("Java", "")
        return self.text_to_preprocess
