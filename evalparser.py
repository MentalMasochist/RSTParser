## evalparser.py
## Author: Yangfeng Ji
## Date: 11-05-2014
## Time-stamp: <yangfeng 11/06/2014 01:01:03>

from model import ParsingModel
from tree import RSTTree
from evaluation import Metrics
from ast import literal_eval

def parse(pm, fedus, d_pos, d_dep):
    """ Parse one document using the given parsing model

    :type pm: ParsingModel
    :param pm: an well-trained parsing model

    :type fedus: string
    :param fedus: file name of an document (with segmented EDUs) 
    """
    with open(fedus) as fin:
        edus = fin.read().split('\n')
        if len(edus[-1]) == 0:
            edus.pop()
    pred_rst = pm.sr_parse(edus, d_pos, d_dep)
    return pred_rst


def writebrackets(fname, brackets):
    """ Write the bracketing results into file
    """
    print 'Writing parsing results into file {}'.format(fname)
    with open(fname, 'w') as fout:
        for item in brackets:
            fout.write(str(item) + '\n')


def get_d_pos(pos_fname):
    """ reads part-of-speach file into dict
    """
    with open(pos_fname,'rb') as pos_f:
        d_pos = literal_eval(pos_f.read())
    return d_pos


def get_d_dep(dep_fname):
    """ reads dependency head-set file into dict
    """
    with open(dep_fname,'rb') as dep_f:
        d_dep = literal_eval(dep_f.read())
    return d_dep
   

def evalparser(path='./examples', report=False):
    """ Test the parsing performance

    :type path: string
    :param path: path to the evaluation data

    :type report: boolean
    :param report: whether to report (calculate) the f1 score
    """
    from os import listdir
    from os.path import join as joinpath
    # ----------------------------------------
    # Load the parsing model
    pm = ParsingModel()
    pm.loadmodel("parsing-model.pickle.gz")
    # ----------------------------------------
    # Evaluation
    met = Metrics(levels=['span','nuclearity','relation'])
    # ----------------------------------------
    # Read all files from the given path
    doclist = [joinpath(path, fname) for fname in listdir(path) if fname.endswith('.edus')]
    for fedus in doclist:
        # ----------------------------------------
        # Parsing
        fpos = fedus + ".pos"
        d_pos = get_d_pos(fpos)
        fdep = fedus + ".dep"
        d_dep = get_d_dep(fdep)
        pred_rst = parse(pm, fedus=fedus, d_pos=d_pos, d_dep=d_dep)
        # Get brackets from parsing results
        pred_brackets = pred_rst.bracketing()
        fbrackets = fedus.replace('edus', 'brackets')
        writebrackets(fbrackets, pred_brackets)
        # ----------------------------------------
        # Evaluate with gold RST tree
        if report:
            fdis = fedus.replace('edus', 'dis')
            gold_rst = RSTTree(fname=fdis)
            gold_rst.build()
            gold_brackets = gold_rst.bracketing()
            met.eval(gold_rst, pred_rst)
    if report:
        met.report()
