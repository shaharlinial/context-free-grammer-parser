from util.tree.list import List
from util.tree.util import flatten

def get_yield(node):
    ''' 
    a function extracting the leaves of a parse tree: assuming the tree is a 
    well-formed parse tree, this is the same as extracting the yield of the tree.
    '''
    
    if isinstance(node, List): 
        return flatten([get_yield(child) for child in node.children])
    else:
        return [node]