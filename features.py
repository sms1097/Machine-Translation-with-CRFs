import libitg
from libitg import Symbol, Terminal, Nonterminal, Span
from libitg import Rule, CFG
from libitg import FSA
from inside_outside import *
from collections import defaultdict
import numpy as np

def get_terminal_string(symbol: Symbol):
    """Returns the python string underlying a certain terminal (thus unwrapping all span annotations)"""
    if not symbol.is_terminal():
        raise ValueError('I need a terminal, got %s of type %s' % (symbol, type(symbol)))
    return symbol.root().obj()

def get_bispans(symbol: Span):
    """
    Returns the bispans associated with a symbol. 
    
    The first span returned corresponds to paths in the source FSA (typically a span in the source sentence),
     the second span returned corresponds to either
        a) paths in the target FSA (typically a span in the target sentence)
        or b) paths in the length FSA
    depending on the forest where this symbol comes from.
    """
    if not isinstance(symbol, Span):
        raise ValueError('I need a span, got %s of type %s' % (symbol, type(symbol)))
    s, start2, end2 = symbol.obj()  # this unwraps the target or length annotation
    _, start1, end1 = s.obj()  # this unwraps the source annotation
    return (start1, end1), (start2, end2)

def simple_features(edge: Rule, src_fsa: FSA, eps=Terminal('-EPS-'), 
                    sparse_del=False, sparse_ins=False, sparse_trans=False,
                   ch_en=defaultdict(lambda:defaultdict()), 
                   en_ch=defaultdict(lambda:defaultdict())) -> dict:
    """
    Featurises an edge given
        * rule and spans
        * src sentence as an FSA
        * TODO: target sentence length n
        * TODO: extract IBM1 dense features
    crucially, note that the target sentence y is not available!    
    """
    fmap = defaultdict(float)
    fset = set() # stores the features we've added
    if len(edge.rhs) == 2:  # binary rule
        fmap['type:binary'] += 1.0
        fset.add('type:binary')
        # here we could have sparse features of the source string as a function of spans being concatenated
        (ls1, ls2), (lt1, lt2) = get_bispans(edge.rhs[0])  # left of RHS
        (rs1, rs2), (rt1, rt2) = get_bispans(edge.rhs[1])  # right of RHS        
        
        # TODO: double check these, assign features, add some more
        if ls1 == ls2:  # deletion of source left child
            fmap['type:deletion-slc'] += 1.0
            fset.add('type:deletion-slc')
        if rs1 == rs2:  # deletion of source right child
            fmap['type:deletion-src'] += 1.0
            fset.add('type:deletion-src')
        if ls2 == rs1:  # monotone
            fmap['type:monotone'] += 1.0
            fset.add('type:monotone')
        if ls1 == rs2:  # inverted
            fmap['type:inverted'] += 1.0
            fset.add('type:inverted')
            
        
        # source span feature of rhs
        src_span_lc = ls2 - ls1
        src_span_rc = rs2 - rs1
        fmap['span:rhs:src-lc:{}'.format(src_span_lc)] += 1.0
        fmap['span:rhs:src-rc:{}'.format(src_span_rc)] += 1.0
        fset.update({'span:rhs:src-lc:{}'.format(src_span_lc),
                  'span:rhs:src-rc:{}'.format(src_span_rc)})
        # target span feature of rhs
        tgt_span_lc = lt2 - lt1
        tgt_span_rc = rt2 - rt1
        fmap['span:rhs:tgt-lc:{}'.format(tgt_span_lc)] += 1.0
        fmap['span:rhs:tgt-rc:{}'.format(tgt_span_rc)] += 1.0
        fset.update({'span:rhs:tgt-lc:{}'.format(tgt_span_lc),
                  'span:rhs:tgt-rc:{}'.format(tgt_span_rc)})
        
    else:  # unary
        symbol = edge.rhs[0]
        if symbol.is_terminal():  # terminal rule
            fmap['type:terminal'] += 1.0
            fset.add('type:terminal')
            # we could have IBM1 log probs for the traslation pair or ins/del
            (s1, s2), (t1, t2) = get_bispans(symbol)
            src_word = src_fsa.label(s1, s2)
            tgt_word = get_terminal_string(symbol)
            if symbol.root() == eps:  # symbol.root() gives us a Terminal free of annotation
                fmap['type:deletion'] += 1.0
                fset.add('type:deletion')
                # dense versions (for initial development phase)
                fmap['ibm1:del:logprob'] += np.log(en_ch[src_word]['<NULL>'])
                
                # sparse version
                if sparse_del:
                    fmap['del:%s' % src_word] += 1.0
                    fset.add('del:%s' % src_word)
            else:                
                if s1 == s2:  # has not consumed any source word, must be an eps rule
                    fmap['type:insertion'] += 1.0
                    fset.add('type:insertion')
                    # dense version
                    fmap['ibm1:ins:logprob'] += np.log(ch_en['<NULL>'][tgt_word])
                    
                    # sparse version
                    if sparse_ins:
                        fmap['ins:%s' % tgt_word] += 1.0
                        fset.add('ins:%s' % tgt_word)
                else:
                    fmap['type:translation'] += 1.0
                    fset.add('type:translation')
                    # dense version
                    fmap['ibm1:x2y:logprob'] += np.log(ch_en[src_word][tgt_word])  # y is english word 
                    fmap['ibm1:y2x:logprob'] += np.log(en_ch[tgt_word][src_word])
                    
                    # sparse version                    
                    if sparse_trans:
                        fmap['trans:%s/%s' % (src_word, tgt_word)] += 1.0
                        fset.add('trans:%s/%s' % (src_word, tgt_word))
        
            # source span feature of rhs
            src_span = s2 - s1
            fmap['span:rhs:src:{}'.format(src_span)] += 1.0
            fset.add('span:rhs:src:{}'.format(src_span))
            # target span feature of rhs
            tgt_span = t2 - t1
            fmap['span:rhs:tgt:{}'.format(tgt_span)] += 1.0
            fset.add('span:rhs:tgt:{}'.format(tgt_span))
                
        else:  # S -> X
            fmap['top'] += 1.0
            fset.add('top')

        # bispans of lhs of edge for source and target (source and target sentence lengths)
        if isinstance(edge.lhs.obj()[0], Span): # exclude the (Nonterminal('D(x)'), 0, 2) rules
            (s1, s2), (t1, t2) = get_bispans(edge.lhs)
            # source span feature of lhs
            src_span = s2 - s1
            fmap['span:lhs:src:{}'.format(src_span)] += 1.0
            fset.add('span:lhs:src:{}'.format(src_span))
            # target span feature of lhs
            tgt_span = t2 - t1
            fmap['span:lhs:tgt:{}'.format(tgt_span)] += 1.0
            fset.add('span:lhs:tgt:{}'.format(tgt_span))

    return fmap, fset

def featurize_edges(forest, src_fsa, 
                    sparse_del=False, sparse_ins=False, sparse_trans=False,
                    eps=Terminal('-EPS-')) -> dict:
    edge2fmap = defaultdict()
    fset_accum = set()
    for edge in forest:
        edge2fmap[edge], fset = simple_features(edge, src_fsa, eps, sparse_del, sparse_ins, sparse_trans)
        fset_accum.update(fset)
    return edge2fmap, fset_accum


def weight_function(edge, fmap, wmap) -> float:
    # dot product of fmap and wmap  (working in log-domain)
    dot = 0.0
    for feature, value in fmap.items():
        dot += value * wmap[feature]
    return dot

def expected_feature_vector(forest: CFG, inside: dict, outside: dict, edge_features: dict) -> dict:
    """Returns an expected feature vector (here a sparse python dictionary)"""
    expected_features = defaultdict(lambda:defaultdict(float))
    for rule in forest:
        k = outside[rule.lhs]
        for symbol in rule.rhs:
            k *= inside[symbol]
        for feature in edge_features[rule]:
            expected_features[rule][feature] = k * edge_features[rule][feature]
    return expected_features
