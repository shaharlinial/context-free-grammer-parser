from cd.rules import Grammar, Tree

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
        this.span = span


def probabilistic_cky(words,grammar):
    table = [[{} for x in range(len(words))] for y in range(len(words))]
    back = [[{} for x in range(len(words))] for y in range(len(words))]
    rules_dictionary = grammar.rules_dictionary
    for j, word in enumerate(words):
        print("j = "+str(j))
        for grammar_rule in rules_dictionary.values():
            rule_node = grammar_rule.rule.head.next
            if rule_node.is_terminal and rule_node.tag == word:
                rule_key = grammar_rule.rule.head.tag
                cky_node = CkyNode(grammar_rule.rule.head.tag, grammar_rule, grammar_rule.probability, (j, j+1))
                new_dict = {rule_key: cky_node}
                table[j][j].update(new_dict)
                print("table["+str(j)+"]["+str(j)+"] = "+rule_key)
        for i in range(j-1, -1, -1):
            print("i = "+str(i))
            for k in range(i+1, j+1, 1):
                print("k = "+str(k))
                for left_node in table[i][k-1].values():
                    left_tag = left_node.grammar_rule.rule.head.tag
                    print("left tag = "+left_tag)
                    for right_node in table[k][j].values():
                        right_tag = right_node.grammar_rule.rule.head.tag
                        print("right tag = "+right_tag)
                        for head, rule_set in grammar.heads_pointers.items():
                            key = head+"->"+left_tag+" "+right_tag
                            if key in rules_dictionary:
                                print("rule = "+key)
                                grammar_rule = rules_dictionary[key]
                                p2 = grammar_rule.probability * left_node.probability * right_node.probability
                                print("table["+str(i)+"]["+str(j)+"] :")
                                for var in table[i][j]:
                                    print(var)
                                if head in table[i][j]:
                                    head_cky_node = rules_dictionary[i][j][head]
                                    p1 = head_cky_node.probability
                                    if p1 < p2:
                                        table[i][j][head] = CkyNode(head_cky_node.tag, grammar_rule, p2, (i, j+1), left_node, right_node)
                                        back[i][j] = {head: [k, left_node, right_node]}
                                        print("add to table[" + str(i) + "][" + str(j) + "] :"+head)
                                else:
                                    # put new rule in table[i][j]
                                    table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j+1), left_node, right_node)
                                    back[i][j] = {head: [k, left_node, right_node]}
                                    print("add to table[" + str(i) + "][" + str(j) + "] :" + head)
        # TODO return BUILD TREE(back[1, LENGTH(words), S]), table[1, LENGTH(words), S]
    print("------------------------- done!-----------------------")


g = Grammar()
for sentence in a_sentences:
    g.build_grammar_from_tree(Tree().parse_tree(None, sentence))
g.calculate_probabilities()
g.binarise(g.rules_dictionary)
g.percolate(g.rules_dictionary)
new_sentence = ["AIF", "LA", "NPGE", "yyDOT"]

probabilistic_cky(new_sentence, g)
