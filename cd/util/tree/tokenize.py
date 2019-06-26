def consume_tag(sequence, pos):
    tag = ''
    while sequence[pos] != ' ' and sequence[pos] != ')' and pos < len(sequence):
        tag += sequence[pos]
        pos += 1
        
    return tag, pos
        

def tokenize(sequence):
    ''' tokenizes the bracketed notation '''
    
    tokens = []
    pos = 0
    while pos < len(sequence):
        current = sequence[pos]
        if current == '(' or current == ')': 
            tokens.append(current)
            pos += 1
        elif current == ' ':
            pos += 1
        else:
            tag, pos = consume_tag(sequence, pos)
            tokens.append(tag)
            
    return tokens
        


            
            