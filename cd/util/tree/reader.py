from util.tree.list import List

def reader(tokens):
    ''' 
    from a *tokenized* bracketed list, derives a tree of tags lists.
    this function does not derive the actual tree
    '''
    list_tree_root = List(None)
    tokens = iter(tokens)

    token = next(tokens)
    if token != '(':
        raise InvalidBracketedList()
    else:    
        _read_group(list_tree_root, tokens)
        list_tree_root = list_tree_root.children[0] # discard initial synthetic root
        return list_tree_root



def _is_tag(token):
    """ if it's not a bracket, it's a tag """
    return token != '(' and token != ')'


class InvalidBracketedList(Exception):
    pass


class Context():
    def __init__(self, parent, token_iterator):
        self.parent         = parent
        self.token_iterator = token_iterator
        
        
def _read_group(parent, token_iterator):
    _start(Context(parent, token_iterator))

    
def _start(context):
    token = next(context.token_iterator, None)
    
    # a group should start with something
    if not token: raise InvalidBracketedList
        
    # a group should start with a head tag
    if token == '(': raise InvalidBracketedList
    if token == ')': raise InvalidBracketedList

    if _is_tag(token):
        context.list = List(head = token)      # new list, with a head
        context.parent.add_child(context.list)    # connect parent list to new list
        _consume_first_child(context)          # proceed with consuming the input group


def _consume_first_child(context):
    token = next(context.token_iterator, None)
    # a group should contain at least one child
    if not token: raise InvalidBracketedList
    _consume(context, token)
    

def _consume(context, token):
    if not token: return 
        
    if _is_tag(token):
        context.list.add_child(token) # add token to current list
        _consume(context, next(context.token_iterator, None))

    elif token == '(':
        _read_group(context.list, context.token_iterator)
        _consume(context, next(context.token_iterator, None))
            
    elif token == ')':
        _group_end(context)
        
    
def _group_end(context):
    return True 

