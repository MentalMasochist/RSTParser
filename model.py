## model.py
## Author: Yangfeng Ji
## Date: 09-09-2014
## Time-stamp: <yangfeng 11/05/2014 20:44:25>

""" As a parsing model, it includes the following functions
1, Mini-batch training on the data generated by the Data class
2, Shift-Reduce RST parsing for a given text sequence
3, Save/load parsing model
"""

from sklearn.svm import LinearSVC
from cPickle import load, dump
from parser import SRParser
from feature import FeatureGenerator
from tree import RSTTree
from util import *
from datastructure import ActionError
import gzip, sys

class ParsingModel(object):
    def __init__(self, vocab=None, idxlabelmap=None, clf=None):
        """ Initialization
        
        :type vocab: dict
        :param vocab: mappint from feature templates to feature indices

        :type idxrelamap: dict
        :param idxrelamap: mapping from parsing action indices to
                           parsing actions

        :type clf: LinearSVC
        :param clf: an multiclass classifier from sklearn
        """
        self.vocab = vocab
        # print labelmap
        self.labelmap = idxlabelmap
        if clf is None:
            self.clf = LinearSVC()


    def train(self, trnM, trnL):
        """ Perform batch-learning on parsing model
        """
        self.clf.fit(trnM, trnL)


    def predict(self, features):
        """ Predict parsing actions for a given set
            of features

        :type features: list
        :param features: feature list generated by
                         FeatureGenerator
        """
        vec = vectorize(features, self.vocab)
        label = self.clf.predict(vec)
        # print label
        return self.labelmap[label[0]]


    def savemodel(self, fname):
        """ Save model and vocab
        """
        if not fname.endswith('.gz'):
            fname += '.gz'
        D = {'clf':self.clf, 'vocab':self.vocab,
             'idxlabelmap':self.labelmap}
        with gzip.open(fname, 'w') as fout:
            dump(D, fout)
        print 'Save model into file: {}'.format(fname)


    def loadmodel(self, fname):
        """ Load model
        """
        with gzip.open(fname, 'r') as fin:
            D = load(fin)
        self.clf = D['clf']
        self.vocab = D['vocab']
        self.labelmap = D['idxlabelmap']
        print 'Load model from file: {}'.format(fname)


    def sr_parse(self, texts, d_pos, d_dep):
        """ Shift-reduce RST parsing based on model prediction

        :type texts: list of string
        :param texts: list of EDUs for parsing
        """
        # Initialize parser
        srparser = SRParser([],[])
        srparser.init(texts, d_pos, d_dep)
        # Parsing
        while not srparser.endparsing():
            # Generate features
            stack, queue = srparser.getstatus()
            # Make sure call the generator with
            # same arguments as in data generation part
            fg = FeatureGenerator(stack, queue)
            features = fg.features()
            label = self.predict(features)
            action = label2action(label)
            # The best choice here is to choose the first
            #   legal action
            try:
                srparser.operate(action)
            except ActionError:
                print "Parsing action error with {}".format(action)
                sys.exit()
        tree = srparser.getparsetree()
        rst = RSTTree(tree=tree)
        return rst
            
