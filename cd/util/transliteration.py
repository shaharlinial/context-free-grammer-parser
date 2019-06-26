'''
Utility functions for handling the transliteration used in this treebank
'''

_hebrew = (" \" % " + ' ת ש ר ק צ פ ע ס נ מ ל כ י ט ח ז ו ה ד ג ב א ').split(' ')[::-1]
_trans  = (' A B G D H W Z X J I K L M N S E P C Q R F T ' + ' O U ').split(' ')
assert len(_hebrew) == len(_trans)

_hebrew_symbols = ' , : ( \" . - ) ! ? ; … '.split(' ')
_trans_symbols  = ' yyCM yyCLN yyLRB yyQUOT yyDOT yyDASH yyRRB yyEXCL yyQM yySCLN yyELPS '.split(' ')
assert len(_hebrew_symbols) == len(_trans_symbols)

def to_heb(s):
    ''' turns transliterated token into hebrew '''
    if s in _trans_symbols:
        return _hebrew_symbols[_trans_symbols.index(s)]
    else:
        return to_heb_phonetic(s)

def to_heb_phonetic(s):
    ''' turns transliterated string into hebrew, assuming the string is not a special tag '''
    result = ''
    for letter in s:
        result += _hebrew[_trans.index(letter)]
    
    return result

        
def to_trans(s):
    ''' transliterates hebrew string '''
    result = ''
    for letter in s:
        result += _trans[_hebrew.index(letter)]
    
    return result


