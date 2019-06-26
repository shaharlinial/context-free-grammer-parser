from util.tree.tokenize import tokenize
from util.tree.reader import reader
from util.tree.node import Node
from util.tree.list import List


def node_tree_from_sequence(sequence):
    ''' transforms a bracketed notation parse into a regular tree from '''
    list_tree = list_tree_from_sequence(sequence)
    return unpack_list_tree(list_tree)
    

def unpack_list_tree(list_node):
    if isinstance(list_node, List):
        node = Node(list_node.head)
        for child in list_node.children:
            node.add_child(unpack_list_tree(child))

    else:
        node = Node(list_node)
        
    return node

    
def list_tree_from_sequence(sequence):
    ''' transforms a bracketed notation parse into a list tree'''
    tokens = tokenize(sequence)
    list_tree = reader(tokens)
    return list_tree