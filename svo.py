import nltk
from nltk.tree import *
from nltk.parse import stanford
from nltk.parse import CoreNLPParser
import nltk.data
import nltk.draw
import os

os.environ['STANFORD_PARSER'] = ''
os.environ['STANFORD_MODELS'] = ''

nltk.data.path.append("D:\\data\\nltk_data")

class SVO(object):
    """
    Class Methods to Extract Subject Verb Object Tuples from a Sentence
    """

    def __init__(self):
        """
        Initialize the SVO Methods
        """
        self.noun_types = ["NN", "NNP", "NNPS", "NNS", "PRP"]
        self.verb_types = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        self.adjective_types = ["JJ", "JJR", "JJS"]
        self.pred_verb_phrase_siblings = None
        jar = r'D:\data'
        model = r'your_path/stanford-postagger-full-2016-10-31/models/english-left3words-distsim.tagger'
        self.parser = CoreNLPParser(url='http://localhost:9000')
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    def get_attributes(self, node, parent_node, parent_node_siblings):
        """
        returns the Attributes for a Node
        """

    def get_subject(self, sub_tree):
        """
        Returns the Subject and all attributes for a subject, sub_tree is a Noun Phrase

        :param sub_tree:
        :return:
        """
        sub_nodes = sub_tree.subtrees()
        sub_nodes = [each for each in sub_nodes if each.pos()]
        subject = None

        for each in sub_nodes:

            if each.label() in self.noun_types:
                subject = each.leaves()
                break

        return {'subject': subject}

    def get_object(self, sub_tree):
        """
        Returns an Object with all attributes of an object
        """
        siblings = self.pred_verb_phrase_siblings
        Object = None
        for each_tree in sub_tree:
            if each_tree.label() in ["NP", "PP"]:
                sub_nodes = each_tree.subtrees()
                sub_nodes = [each for each in sub_nodes if each.pos()]

                for each in sub_nodes:
                    if each.label() in self.noun_types:
                        Object = each.leaves()
                        break
                break
            else:
                sub_nodes = each_tree.subtrees()
                sub_nodes = [each for each in sub_nodes if each.pos()]
                for each in sub_nodes:
                    if each.label() in self.adjective_types:
                        Object = each.leaves()
                        break
                # Get first noun in the tree
        self.pred_verb_phrase_siblings = None
        return {'object': Object}

    def get_predicate(self, sub_tree):
        """
        Returns the Verb along with its attributes, Also returns a Verb Phrase

        :param sub_tree:
        :return:
        """

        sub_nodes = sub_tree.subtrees()
        sub_nodes = [each for each in sub_nodes if each.pos()]
        predicate = None
        sub_tree = ParentedTree.convert(sub_tree)
        for each in sub_nodes:
            if each.label() in self.verb_types:
                sub_tree = each
                predicate = each.leaves()

        # get all predicate_verb_phrase_siblings to be able to get the object
        sub_tree = ParentedTree.convert(sub_tree)
        if predicate:
            pred_verb_phrase_siblings = self.tree_root.subtrees()
            pred_verb_phrase_siblings = [each for each in pred_verb_phrase_siblings if
                                         each.label() in ["NP", "PP", "ADJP", "ADVP"]]
            self.pred_verb_phrase_siblings = pred_verb_phrase_siblings

        return {'predicate': predicate}

    def process_parse_tree(self, parse_tree):
        """
        Returns the Subject-Verb-Object Representation of a Parse Tree.
        Can Vary depending on number of 'sub-sentences' in a Parse Tree
        """
        self.tree_root = parse_tree
        # Step 1 - Extract all the parse trees that start with 'S'
        output_list = []
        output_dict = {}

        for idx, subtree in enumerate(parse_tree[0].subtrees()):
            subject = None
            predicate = None
            Object = None
            if subtree.label() in ["S", "SQ", "SBAR", "SBARQ", "SINV", "FRAG"]:
                children_list = subtree
                children_values = [each_child.label() for each_child in children_list]
                children_dict = dict(zip(children_values, children_list))

                # Extract Subject, Verb-Phrase, Objects from Sentence sub-trees
                if children_dict.get("NP") is not None:
                    subject = self.get_subject(children_dict["NP"])

                if children_dict.get("VP") is not None:
                    # Extract Verb and Object
                    # i+=1
                    # """
                    # if i==1:
                    #    pdb.set_trace()
                    # """
                    predicate = self.get_predicate(children_dict["VP"])
                    Object = self.get_object(children_dict["VP"])

                try:
                    if subject['subject'] and predicate['predicate'] and Object['object']:
                        output_dict['subject'] = subject['subject']
                        output_dict['predicate'] = predicate['predicate']
                        output_dict['object'] = Object['object']
                        output_list.append(output_dict)
                except Exception as e:
                    print(e)
                    continue

        return output_list

    def traverse(self, t):
        try:
            t.label()
        except AttributeError:
            print(t)
        else:
            print('(', t.label())
            for child in t:
                self.traverse(child)

            print(')')

    def sentence_split(self, text):
        """
        returns the Parse Tree of a Sample
        """
        sentences = self.sent_detector.tokenize(text)
        return sentences

    def get_parse_tree(self, sentence):
        """
        returns the Parse Tree of a Sample
        """
        parse_tree = self.parser.raw_parse(sentence)

        return parse_tree

    def List_To_Tree(self, lst):
        if (not isinstance(lst, basestring)):
            if (len(lst) == 2 and isinstance(lst[0], str) and isinstance(lst[1], str)):
                lst = Tree(str(lst[0]).split('+')[0], [str(lst[1])])
            elif (isinstance(lst[0], str) and not isinstance(lst[1], str)):
                lst = Tree(str(lst[0]).split('+')[0], map(self.List_To_Tree, lst[1: len(lst)]))
        return lst