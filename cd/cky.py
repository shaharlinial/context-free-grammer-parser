from mmn13.cd.rules import Grammar, Tree, Node
#from cd.rules import Grammar, Tree

sentences = "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT))),\
(TOP (S (SBAR (S (S (NP (MOD GM) (NP (NN IHWDIM))) (VP (VB NMCAIM)) (ADVP (RB ETH)) (PP (IN EL) (NP (H H) (NN KWWNT)))) (yyQUOT yyQUOT))) (VP (VB AMRW)) (NP (NNT ANFI) (NP (NNP KK))) (PP (IN B) (NP (NNT ET) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))))) (yyDOT yyDOT))),\
(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NISH)) (VP (VB LHSTIR) (NP (PRP ZAT))) (yyDOT yyDOT))),\
(TOP (FRAG (NP (NP (MOD LA) (NP (NP (H H) (NN MNHIGIM)) (SBAR (REL F) (S (VP (VB HSITW)) (PP (IN L) (NP (NN RCX))))))) (CC (yySCLN yySCLN)) (NP (MOD LA) (NP (NP (NN XLQIM)) (PP (IN B) (NP (NP (H H) (NN CIBWR)) (ADJP (H H) (JJ ZH)))) (yyCM yyCM) (SBAR (REL F) (S (PP (IN LAWRK) (NP (NNT CIR) (NP (H H) (NN HLWWIIH)))) (VP (VB RQMW)) (NP (NP (NN TWKNIWT)) (SBAR (SQ (ADVP (QW KICD)) (VP (VB LPGWE) (PP (IN B) (NP (NN ERBIM)))) (PP (MOD KBR) (PP (IN B) (NP (NP (H H) (NN IMIM)) (ADJP (H H) (JJ QRWBIM))))))))))))) (yyDOT yyDOT))),\
(TOP (S (NP (NP (NNT SWPR) (NP (yyQUOT yyQUOT) (NP (NNPP (H H) (NN ARC))) (yyQUOT yyQUOT))) (PP (IN B) (NP (H H) (NN CPWN)))) (yyCM yyCM) (VP (VB MWSIP)) (SBAR (yyCLN yyCLN) (S (NP (NN IRIWT)) (VP (VB NFMEW)) (ADVP (RB ATMWL)) (PP (IN B) (NP (NP (NN FEH)) (NP (CD 2000)) (PP (IN B) (NP (H H) (NN ERB))))) (PP (IN B) (NP (NNP FPREM))) (yyCM yyCM) (ADVP (ADVP (RB SMWK)) (PP (IN L) (NP (NP (NN BITW)) (POS FL) (NP (NP (NNT RAF) (NP (H H) (NN EIRIIH))) (yyCM yyCM) (NP (NNPP (NNP AIBRHIM) (NNPP (NNP NIMR) (NNP XWSIIN)))))))))) (yyDOT yyDOT))),\
(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))"

a_sentences = sentences.split(",")


class CkyNode(object):
    def __init__(self, tag, grammar_rule, probability, span, left_child=None, right_child=None):
        self.tag = tag
        self.grammar_rule = grammar_rule
        # if the child is a terminal arbitrarily save it as a left child
        self.left_child = left_child
        self.right_child = right_child
        self.probability = probability
        self.span = span

def get_max_probability(dictionary):
    max = 0.0
    ckynode = None
    for key,value in dictionary.items():
        if max <= value.probability:
            ckynode = value
            max = value.probability
    return ckynode

def probabilistic_cky(words,grammar):
    # grammar -> Grammar()
    table = [[{} for x in range(len(words))] for y in range(len(words))]
    # table = ROW X COLUMNS table[i][j] -> table[i][j] = {S|VP|...|:CkyNode}
    back = [[{} for x in range(len(words))] for y in range(len(words))]
    # back = later....
    # rules_dictionary = {hash:grammar node} , {"S->VP NN":GrammarNode()}
    rules_dictionary = grammar.rules_dictionary
    # iterate words
    for j, word in enumerate(words):
        # iterate rule
        #for grammar_rule in rules_dictionary.values():
        # fill rule->words
        for head in grammar.heads_pointers:
            # Search for rules of this form: X -> word [terminal]
            # rule_node = y <-> X->y
            search_rule = head + "->" + word
            if search_rule in rules_dictionary:
                grammar_rule = rules_dictionary[search_rule]
                # grammar_rule = X->word
                # rule_key = X
                rule_key = grammar_rule.rule.head.tag
                # "X: X->word"
                to_word = CkyNode(tag=grammar_rule.rule.head.next.tag,
                                  grammar_rule=None,
                                  probability=0.0,
                                  span=None,
                                  left_child=None,
                                  right_child=None)

                cky_node = CkyNode(tag=grammar_rule.rule.head.tag,
                                   grammar_rule=grammar_rule,
                                   probability=grammar_rule.probability,
                                   span=(j, j+1),
                                   left_child=to_word,
                                   right_child=None)


                new_dict = {rule_key: cky_node}
                #table[j][j] = {"s":CkyNode} --> table[j][j] = {"s":CkyNode, "np":CkyNode}
                table[j][j].update(new_dict)

        # second part of algorithm // fill rules->rules
        for i in range(j-1, -1, -1):
            for k in range(i+1, j+1, 1):
                for left_node in table[i][k-1].values():
                    left_tag = left_node.tag
                    for right_node in table[k][j].values():
                        right_tag = right_node.tag
                        for head, rule_set in grammar.heads_pointers.items():
                            key = head+"->"+left_tag+" "+right_tag
                            if key in rules_dictionary:
                                grammar_rule = rules_dictionary[key]
                                p2 = grammar_rule.probability * left_node.probability * right_node.probability
                                if head in table[i][j]:
                                    head_cky_node = table[i][j][head]
                                    p1 = head_cky_node.probability
                                    if p1 < p2:
                                        table[i][j][head] = CkyNode(head_cky_node.tag, grammar_rule, p2, (i, j+1), left_node, right_node)
                                        back[i][j] = {head: [k, left_node, right_node]}
                                else:
                                    # put new rule in table[i][j]
                                    table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j+1), left_node, right_node)
                                    back[i][j] = {head: [k, left_node, right_node]}

    # Building tree.
    # phase 1: select max probability root ->
    root = get_max_probability(table[0][len(words) - 1])

    tree_head = Tree()
    # phase 2: -> recursively build left and right children
    tree_head.build_tree_from_cky_root_node(root)
    print("y")

    # TODO return BUILD TREE(back[1, LENGTH(words), S]), table[1, LENGTH(words), S]
    print("------------------------- done!-----------------------")

from tqdm import tqdm
g = Grammar()

#g.build_grammar_from_tree(Tree().parse_tree(None, "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT)))"))
with open('data/heb-ctrees_small.train', 'r') as train_set:
    for sentence in tqdm(train_set.readlines()):
        g.build_grammar_from_tree(Tree().parse_tree(None, sentence))


g.calculate_probabilities()
g.binarise()
g.percolate()
new_sentence = "AIF LA NPGE yyDOT".split(" ")
#(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))
new_sentence1 = "XBL yyDOT".split(" ")
#(TOP (FRAG (INTJ (ADVP (RB XBL))) (yyDOT yyDOT)))
new_sentence2 = "MSTBR F HIITI TMIM yyDOT".split(" ")
#(TOP (S (VP (VB MSTBR)) (SBAR (COM F) (S (AUX HIITI) (PREDP (ADJP (JJ TMIM))))) (yyDOT yyDOT)))

#probabilistic_cky(new_sentence, g)
#probabilistic_cky(new_sentence1, g)
probabilistic_cky(new_sentence2, g)



