from mmn13.cd.rules import Grammar, Tree
from mmn13.cd.cky import CkyNode, get_max_probability
import time
import math


def probabilistic_unary_cky(words, grammar):
    # grammar -> Grammar()
    t1 = time.time()

    table = [[{} for x in range(len(words))] for y in range(len(words))]
    # table = ROW X COLUMNS table[i][j] -> table[i][j] = {S|VP|...|:CkyNode}
    # rules_dictionary = {hash:grammar node} , {"S->VP NN":GrammarNode()}
    rules_dictionary = grammar.rules_dictionary
    # iterate words
    for j, word in enumerate(words):
        # fill rule->words
        try:
            rules = grammar.tails_pointers[word]
            for r in rules:
                grammar_rule = rules_dictionary[r]
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
                                   probability=math.log2(grammar_rule.probability),
                                   span=(j, j + 1),
                                   left_child=to_word,
                                   right_child=None)
                new_dict = {rule_key: cky_node}
                # table[j][j] = {"s":CkyNode} --> table[j][j] = {"s":CkyNode, "np":CkyNode}
                table[j][j].update(new_dict)
            print("Finished [%d][%d] in %s seconds" % (j, j, str(time.time() - t1)))
        except KeyError:

            # We thought that it would have been a great idea, smoothing unknown words
            # using features like we did in MMN 12 and HMM decoding,
            # But since words are transliterated from english to hebrew,
            # it seem a bit pointless to write a probability matrix for a NON-Terminal -> Terminal rule
            # without knowing any structural information about the words.
            # Eventually we went with Laplace smoothing "NFRM" | VP->NFRM , S->NFRM ... with probability of 1/|Grammar|

            # Example: given word "NFRM" which there are no rules that generate this word.
            # Vocabulary = All Word is Grammar [TOP->"alo", X->"alo"]  equals to 1 <-> iterate 1 time tails
            # pointer
            # add +1 for each tail that doesnt contain '|'
            # so V = |Vocabulary|
            # count each POS Rule and save as q_i
            # if unknown words -> probability for each tag i is 1 / V+q_i
            # if known word -> probability is count(POS Rule) + 1 / V+q_i
            # Note: must be done prior to binarise and percolate
            for rule_key, unknown_grammar_node in grammar.unknown_words.items():
                rule_key = unknown_grammar_node.rule.head.tag
                # "X: X->#"
                to_word = CkyNode(tag=word,
                                  grammar_rule=None,
                                  probability=0.0,
                                  span=None,
                                  left_child=None,
                                  right_child=None)
                cky_node = CkyNode(tag=unknown_grammar_node.rule.head.tag,
                                   grammar_rule=unknown_grammar_node,
                                   probability=math.log2(unknown_grammar_node.probability),
                                   span=(j, j + 1),
                                   left_child=to_word,
                                   right_child=None)
                new_dict = {rule_key: cky_node}
                # table[j][j] = {"s":CkyNode} --> table[j][j] = {"s":CkyNode, "np":CkyNode}
                table[j][j].update(new_dict)
            print("Finished [%d][%d] in %s seconds" % (j, j, str(time.time() - t1)))

        stack = list()
        for cky_node in table[j][j].values():
            stack.append(cky_node)
        while len(stack) > 0:
            cky_node = stack.pop()
            rules = grammar.tails_pointers[cky_node.tag]
            for r in rules:
                grammar_rule = rules_dictionary[r]
                p2 = math.log2(grammar_rule.probability) + cky_node.probability
                head = grammar_rule.rule.head.tag
                if head in table[j][j]:
                    head_cky_node = table[j][j][head]
                    p1 = head_cky_node.probability
                    if p1 < p2:
                        new_cky_node = CkyNode(head, grammar_rule, p2, cky_node.span, cky_node)
                        table[j][j][head] = new_cky_node
                        stack.append(new_cky_node)
                else:
                    new_cky_node = CkyNode(head, grammar_rule, p2, cky_node.span, cky_node)
                    table[j][j][head] = new_cky_node
                    stack.append(new_cky_node)

        # second part of algorithm // fill rules->rules
        for i in range(j - 1, -1, -1):
            for k in range(i + 1, j + 1, 1):
                # process binary rules
                for left_node in table[i][k - 1].values():
                    left_tag = left_node.tag
                    for right_node in table[k][j].values():
                        right_tag = right_node.tag
                        key = left_tag + "|" + right_tag
                        rules = []
                        if key in grammar.tails_pointers:
                            rules = grammar.tails_pointers[key]  # o(1)
                        for r in rules:
                            grammar_rule = rules_dictionary[r]
                            p2 = math.log2(grammar_rule.probability) + left_node.probability + right_node.probability
                            head = grammar_rule.rule.head.tag
                            if head in table[i][j]:
                                head_cky_node = table[i][j][head]
                                p1 = head_cky_node.probability
                                if p1 < p2:
                                    table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j + 1), left_node,
                                                                right_node)
                            else:
                                # put new rule in table[i][j]
                                table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j + 1), left_node, right_node)

            # process unary rules - look for A->B (cky_node) in table[i][j] rules. add A to table[i][j] with pointer to B

            stack = list()
            for cky_node in table[i][j].values():
                stack.append(cky_node)
            while len(stack) > 0:
                cky_node = stack.pop()
                rules = grammar.tails_pointers[cky_node.tag]
                for r in rules:
                    grammar_rule = rules_dictionary[r]
                    p2 = math.log2(grammar_rule.probability) + cky_node.probability
                    head = grammar_rule.rule.head.tag
                    if head in table[i][j]:
                        head_cky_node = table[i][j][head]
                        p1 = head_cky_node.probability
                        if p1 < p2:
                            new_cky_node = CkyNode(head, grammar_rule, p2, cky_node.span, cky_node)
                            table[i][j][head] = new_cky_node
                            stack.append(new_cky_node)
                    else:
                        new_cky_node = CkyNode(head, grammar_rule, p2, cky_node.span, cky_node)
                        table[i][j][head] = new_cky_node
                        stack.append(new_cky_node)

    # Building tree.
    # phase 1: select max probability root ->
    root = get_max_probability(table[0][len(words) - 1])

    tree = Tree()
    # phase 2: -> recursively build left and right children
    tree.build_tree_from_cky_root_node(root)

    tree.de_binarise()

    return tree


g = Grammar()


# sentences = "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT))),\
# (TOP (S (SBAR (S (S (NP (MOD GM) (NP (NN IHWDIM))) (VP (VB NMCAIM)) (ADVP (RB ETH)) (PP (IN EL) (NP (H H) (NN KWWNT)))) (yyQUOT yyQUOT))) (VP (VB AMRW)) (NP (NNT ANFI) (NP (NNP KK))) (PP (IN B) (NP (NNT ET) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))))) (yyDOT yyDOT))),\
# (TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NISH)) (VP (VB LHSTIR) (NP (PRP ZAT))) (yyDOT yyDOT))),\
# (TOP (FRAG (NP (NP (MOD LA) (NP (NP
# (H H) (NN MNHIGIM)) (SBAR (REL F) (S (VP (VB HSITW)) (PP (IN L) (NP (NN RCX))))))) (CC (yySCLN yySCLN)) (NP (MOD LA) (NP (NP (NN XLQIM)) (PP (IN B) (NP (NP (H H) (NN CIBWR)) (ADJP (H H) (JJ ZH)))) (yyCM yyCM) (SBAR (REL F) (S (PP (IN LAWRK) (NP (NNT CIR) (NP (H H) (NN HLWWIIH)))) (VP (VB RQMW)) (NP (NP (NN TWKNIWT)) (SBAR (SQ (ADVP (QW KICD)) (VP (VB LPGWE) (PP (IN B) (NP (NN ERBIM)))) (PP (MOD KBR) (PP (IN B) (NP (NP (H H) (NN IMIM)) (ADJP (H H) (JJ QRWBIM))))))))))))) (yyDOT yyDOT))),\
# (TOP (S (NP (NP (NNT SWPR) (NP (yyQUOT yyQUOT) (NP (NNPP (H H) (NN ARC))) (yyQUOT yyQUOT))) (PP (IN B) (NP (H H) (NN CPWN)))) (yyCM yyCM) (VP (VB MWSIP)) (SBAR (yyCLN yyCLN) (S (NP (NN IRIWT)) (VP (VB NFMEW)) (ADVP (RB ATMWL)) (PP (IN B) (NP (NP (NN FEH)) (NP (CD 2000)) (PP (IN B) (NP (H H) (NN ERB))))) (PP (IN B) (NP (NNP FPREM))) (yyCM yyCM) (ADVP (ADVP (RB SMWK)) (PP (IN L) (NP (NP (NN BITW)) (POS FL) (NP (NP (NNT RAF) (NP (H H) (NN EIRIIH))) (yyCM yyCM) (NP (NNPP (NNP AIBRHIM) (NNPP (NNP NIMR) (NNP XWSIIN)))))))))) (yyDOT yyDOT))),\
# (TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))"
#
# a_sentences = sentences.split(",")
#
# for sentences in a_sentences:
#     g.build_grammar_from_tree(Tree().parse_tree(None, sentences))

with open('data/heb-ctrees.train', 'r') as train_set:
    for sentence in train_set.readlines():
        g.build_grammar_from_tree(Tree().parse_tree(None, sentence))

g.calculate_probabilities()
g.binarise()

new_sentence = "AIF LA NPGE yyDOT".split(" ")
hypothesis_tree = probabilistic_unary_cky(new_sentence, g)
ground_truth_tree = Tree()
ground_truth_tree.parse_tree(None, bracket_sentence="(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))")
h_span_set = hypothesis_tree.get_tree_span()
g_span_set = ground_truth_tree.get_tree_span()
intersection = g_span_set.intersection(h_span_set)
print("intersection "+str(len(intersection)))
recall = len(intersection)/len(g_span_set)
precision = len(intersection)/len(h_span_set)
f_score = (2*precision*recall)/(precision + recall)
print("f_score "+str(f_score))
