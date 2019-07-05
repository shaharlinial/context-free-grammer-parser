from mmn13.cd.rules import Grammar, Tree, Node
import math
import time
#from cd.rules import Grammar, Tree



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
    t1 = time.time()
    table = [[{} for x in range(len(words))] for y in range(len(words))]
    # table = ROW X COLUMNS table[i][j] -> table[i][j] = {S|VP|...|:CkyNode}
    # rules_dictionary = {hash:grammar node} , {"S->VP NN":GrammarNode()}
    rules_dictionary = grammar.rules_dictionary
    # iterate words
    for j, word in enumerate(words):
        # iterate rule
        #for grammar_rule in rules_dictionary.values():

        # fill rule->words
        rules = grammar.tails_pointers[word]

        # We thought that it would have been a great idea, smoothing unknown words
        # using features like we did in MMN 12 and HMM decoding,
        # But since words are transliterated from english to hebrew,
        # it seem a bit pointless to write a probability matrix for a NON-Terminal -> Terminal rule
        # without knowing any structural information about the words.
        # Eventually we went with Laplace smoothing "NFRM" | VP->NFRM , S->NFRM ... with probability of 1/|Grammar|


        # TODO: if word doesnt exist in training set , will raise KeyError exception. -> need to be solved with smoothing.
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
                               span=(j, j+1),
                               left_child=to_word,
                               right_child=None)
            new_dict = {rule_key: cky_node}
            #table[j][j] = {"s":CkyNode} --> table[j][j] = {"s":CkyNode, "np":CkyNode}
            table[j][j].update(new_dict)
        print("Finished [%d][%d] in %s seconds" % (j,j, str(time.time() - t1)))
        # second part of algorithm // fill rules->rules
        for i in range(j-1, -1, -1):
            for k in range(i+1, j+1, 1):
                for left_node in table[i][k-1].values():
                    left_tag = left_node.tag
                    for right_node in table[k][j].values():
                        right_tag = right_node.tag
                        key = left_tag + "|" + right_tag
                        rules = []
                        if key in grammar.tails_pointers:
                            rules = grammar.tails_pointers[key] # o(1)
                        for r in rules:
                            grammar_rule = rules_dictionary[r]
                            p2 = math.log2(grammar_rule.probability) + left_node.probability + right_node.probability
                            head = grammar_rule.rule.head.tag
                            if head in table[i][j]:
                                head_cky_node = table[i][j][head]
                                p1 = head_cky_node.probability
                                if p1 < p2:
                                    table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j+1), left_node, right_node)
                            else:
                                # put new rule in table[i][j]
                                table[i][j][head] = CkyNode(head, grammar_rule, p2, (i, j+1), left_node, right_node)

    # Building tree.
    # phase 1: select max probability root ->
    root = get_max_probability(table[0][len(words) - 1])

    tree = Tree()
    # phase 2: -> recursively build left and right children
    tree.build_tree_from_cky_root_node(root)

    tree.de_binarise()

    return tree

from tqdm import tqdm
g = Grammar()

#tree = Tree().parse_tree(None, "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT)))")
#g.build_grammar_from_tree(Tree().parse_tree(None, "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT)))"))
#print("done")
with open('data/heb-ctrees.train', 'r') as train_set:
    for sentence in tqdm(train_set.readlines()):
        g.build_grammar_from_tree(Tree().parse_tree(None, sentence))


g.calculate_probabilities()
#(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))
# l=1  l=2 l=3 l=4       l = 3  l=4    l=3 l=4          l=3 l=4
g.binarise()
g.percolate()
g.populate_tails()


new_sentence = "AIF LA NPGE yyDOT".split(" ")
new_sentence1 = "XBL yyDOT".split(" ")
#(TOP (FRAG (INTJ (ADVP (RB XBL))) (yyDOT yyDOT)))
new_sentence2 = "MSTBR F HIITI TMIM yyDOT".split(" ")
#(TOP (S (VP (VB MSTBR)) (SBAR (COM F) (S (AUX HIITI) (PREDP (ADJP (JJ TMIM))))) (yyDOT yyDOT)))
new_sentence3 = "SEIP MPTX B H MSMK H XWQTI MXIIB AT H MLK yyQUOT LCIIT L H XWQH W LHGN ELI HIA yyQUOT yyDOT".split(" ")


##hypothesis_tree = probabilistic_cky(new_sentence, g)

ground_truth_tree = Tree()
#ground_truth_tree.parse_tree(None, bracket_sentence="(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))")
ground_truth_tree.parse_tree(None, bracket_sentence="(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))")

#h_span_set = hypothesis_tree.get_tree_span()#
#print("h_span_set " + str(len(h_span_set)))
#g_span_set = ground_truth_tree.get_tree_span()
#print("g_span_set " + str(len(g_span_set)))
#intersection = g_span_set.intersection(h_span_set)
#print("intersection "+str(len(intersection)))
#recall = len(intersection)/len(g_span_set)
#precision = len(intersection)/len(h_span_set)
#f_score = (2*precision*recall)/(precision + recall)
#print("f_score "+str(f_score))
#probabilistic_cky(new_sentence1, g)
t = probabilistic_cky(new_sentence3, g)
print(t.print_tree(t.tree.head))
#f_out = open("data/test.tst", "a+")
#with open('data/gold_small_sentences', 'r') as gold_sentences:
#    for sentence in tqdm(gold_sentences.readlines(), "parsing gold sentences"):
#        hypothesis_tree = probabilistic_cky(sentence.split(" "), g)
#        f_out.write(hypothesis_tree.print_tree(hypothesis_tree.tree) + "\n")
#
#f_out.close()
#
#
#