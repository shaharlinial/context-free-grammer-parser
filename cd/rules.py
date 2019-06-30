import copy
sentences = "(TOP (S (yyQUOT yyQUOT) (S (VP (VB THIH)) (NP (NN NQMH)) (CC W) (ADVP (RB BGDWL))) (yyDOT yyDOT))),\
(TOP (S (SBAR (S (S (NP (MOD GM) (NP (NN IHWDIM))) (VP (VB NMCAIM)) (ADVP (RB ETH)) (PP (IN EL) (NP (H H) (NN KWWNT)))) (yyQUOT yyQUOT))) (VP (VB AMRW)) (NP (NNT ANFI) (NP (NNP KK))) (PP (IN B) (NP (NNT ET) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))))) (yyDOT yyDOT))),\
(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NISH)) (VP (VB LHSTIR) (NP (PRP ZAT))) (yyDOT yyDOT))),\
(TOP (FRAG (NP (NP (MOD LA) (NP (NP (H H) (NN MNHIGIM)) (SBAR (REL F) (S (VP (VB HSITW)) (PP (IN L) (NP (NN RCX))))))) (CC (yySCLN yySCLN)) (NP (MOD LA) (NP (NP (NN XLQIM)) (PP (IN B) (NP (NP (H H) (NN CIBWR)) (ADJP (H H) (JJ ZH)))) (yyCM yyCM) (SBAR (REL F) (S (PP (IN LAWRK) (NP (NNT CIR) (NP (H H) (NN HLWWIIH)))) (VP (VB RQMW)) (NP (NP (NN TWKNIWT)) (SBAR (SQ (ADVP (QW KICD)) (VP (VB LPGWE) (PP (IN B) (NP (NN ERBIM)))) (PP (MOD KBR) (PP (IN B) (NP (NP (H H) (NN IMIM)) (ADJP (H H) (JJ QRWBIM))))))))))))) (yyDOT yyDOT))),\
(TOP (S (NP (NP (NNT SWPR) (NP (yyQUOT yyQUOT) (NP (NNPP (H H) (NN ARC))) (yyQUOT yyQUOT))) (PP (IN B) (NP (H H) (NN CPWN)))) (yyCM yyCM) (VP (VB MWSIP)) (SBAR (yyCLN yyCLN) (S (NP (NN IRIWT)) (VP (VB NFMEW)) (ADVP (RB ATMWL)) (PP (IN B) (NP (NP (NN FEH)) (NP (CD 2000)) (PP (IN B) (NP (H H) (NN ERB))))) (PP (IN B) (NP (NNP FPREM))) (yyCM yyCM) (ADVP (ADVP (RB SMWK)) (PP (IN L) (NP (NP (NN BITW)) (POS FL) (NP (NP (NNT RAF) (NP (H H) (NN EIRIIH))) (yyCM yyCM) (NP (NNPP (NNP AIBRHIM) (NNPP (NNP NIMR) (NNP XWSIIN)))))))))) (yyDOT yyDOT))),\
(TOP (S (NP (NN AIF)) (ADVP (RB LA)) (VP (VB NPGE)) (yyDOT yyDOT)))"
from tqdm import tqdm
a_sentences = sentences.split(",")

class Node(object):
    def __init__(self, tag, parent, is_terminal=False):
        self.tag = tag
        self.children = []
        self.parent = parent
        self.is_terminal = is_terminal

    def add_children(self,node):
        self.children.append(node)

class Tree(object):
    def __init__(self, head=None):
        self.tree = head

    @staticmethod
    def parse_string_sequence(string, special_key):
        return string[:string.index(special_key)]

    @staticmethod
    def parse_string_reverse_sequence(string, special_key):
        return string[string.index(special_key) + 1:]

    def parse_tree(self, parent, bracket_sentence):
        if parent is not None and parent.is_terminal == True:
            return

        if '(' not in bracket_sentence and ' 'not in bracket_sentence and ')' not in bracket_sentence:
            return Node(tag=bracket_sentence,
                        parent=parent,
                        is_terminal=True)

        tag = self.parse_string_sequence(bracket_sentence[1:], " ")
        node = Node(tag=tag, parent=parent, is_terminal=False)
        if self.tree is None:
            self.tree = node

        if bracket_sentence.count('(') == 1 and bracket_sentence.count(')') == 1:
            n_node = Node(tag=self.parse_string_reverse_sequence(bracket_sentence[:-1], " "), parent = node, is_terminal = True)
            node.add_children(n_node)
            return node

        idx = 0
        to_idx= 0
        counter = 0
        sentence = bracket_sentence[len(tag)+2:-1]
        for c in sentence:
            to_idx += 1
            if c == "(":
                counter += 1
            if c == ")":
                counter -= 1
            if counter == 0:
                # parse next children [space after rounded brackets] #
                if c == ' ':
                    idx += 1
                    continue
                node.add_children(self.parse_tree(node, sentence[idx:to_idx]))
                idx = to_idx

        return node



    def build_tree_from_ckyrootNode(self, ckynode, parent=None):

        # one time - create root of tree
        if ckynode.left_child is None and ckynode.right_child is None:
            # Todo: could is_terminal be false here?
            return Node(tag=ckynode.tag, parent=parent, is_terminal=True)

        parent = Node(ckynode.tag, parent=parent, is_terminal=False)

        if self.tree is None:
            self.tree = parent

        parent.add_children(self.build_tree_from_ckyrootNode(ckynode.left_child, parent))
        parent.add_children(self.build_tree_from_ckyrootNode(ckynode.right_child, parent))

        return parent

class RuleNode(object):
    def __init__(self, tag, is_head=False, next=None, back=None, is_terminal=False):
        self.tag = tag
        self.is_head = is_head
        self.is_terminal = is_terminal
        self.next = next
        self.back = back

    #returns the current tag chained by following tags "s->nn->jj" ==> "s-nn-jj"
    def chain_tags(self):
        chain = self.tag
        temp = self

        while temp.next is not None:
            chain += ('-' + temp.next.tag)
            temp = temp.next
        return chain

class Rule(object):
    def __init__(self, node, is_reconstructed=False):
        self.head = node
        self.is_reconstructed = is_reconstructed

    def insert(self, node):
        temp = self.head
        while temp.next is not None:
            temp = temp.next
        new_node = node
        temp.next = new_node
        new_node.back = temp

    def hash(self):
        temp = self.head
        hash_key = temp.tag + "->"
        while temp.next is not None:
            temp = temp.next
            hash_key += temp.tag
            if temp.next is not None:
                hash_key += " "
        return hash_key

    # to prevent NP->NP | SBAR->SBAR
    def is_circular(self):
        if self.head.next is None:
            return False
        if self.head.tag == self.head.next.tag:
            if self.head.next.is_terminal:
                return False
            else:
                return True
        return False

    def __len__(self):
        if self.head is None:
            return 0
        len = 1
        temp = self.head
        while temp.next is not None:
            len += 1
            temp = temp.next
        return len

class GrammarNode(object):
    def __init__(self, rule, count, probability=0.0):
        self.rule = rule
        self.count = count
        self.probability = probability

class Grammar(object):
    def __init__(self):
        self.heads_count = dict() # "{s:80, np:90}"
        self.heads_pointers = dict() # "{s:set("s->vp nn","s->yyqout yyquot"...)}"
        self.tails_pointers = dict() # "{jj-kk-mm: set("x->y jj-kk-mm..")}
        self.rules_dictionary = dict()  # 'hash(rule):grammar_node'


    def build_grammar_from_tree(self, tree_head):
        #process tree... -> self.rule_list = TREE_PROCCESSED
        node = tree_head
        if node is None or node.is_terminal:
            return

        rule = Rule(RuleNode(tag=node.tag, is_head=True))
        for children in node.children:
            rule.insert(RuleNode(tag=children.tag,
                                 is_head=False,
                                 is_terminal=children.is_terminal))

        grammar_key = rule.hash()
        if rule.head.tag in self.heads_count:
            self.heads_count[rule.head.tag] += 1
        else:
            self.heads_count[rule.head.tag] = 1

        if grammar_key in self.rules_dictionary:
            self.rules_dictionary[grammar_key].count += 1
        else:
            self.rules_dictionary[grammar_key] = GrammarNode(rule, count=1)

        if rule.head.tag not in self.heads_pointers:
            self.heads_pointers[rule.head.tag] = set()

        self.heads_pointers[rule.head.tag].add(grammar_key)
        for child in node.children:
            self.build_grammar_from_tree(child)

    def calculate_probabilities(self):
        for key, grammar_rule in self.rules_dictionary.items():
            grammar_rule.probability = grammar_rule.count / self.heads_count[grammar_rule.rule.head.tag]

    def binarise(self, grammar_dictionary):
        #{s -> nn jj kk } PROB: 0.5
        # s->nn JJKK PROB:0.5
        # np-> nn jj kk PROB:0.4
        # np -> nn JJKK PROB: 0.4
        # JJKK -> jj kk PROB: 1
        # s -> NP PROB: 0.3
        # NP -> vp nn PROB: 0.6
        # s-> vp nn 0.3*0.6
        #[Rule,Rule,Rule...]
        stack = list()
        grammar = dict()

        for key, grammar_node in grammar_dictionary.items():
            stack.append(grammar_node)

        while len(stack) > 0:
            # {s -> nn jj kk } PROB: 0.5
            # {s -> nn jj kk}
            grammar_node = stack.pop()
            if len(grammar_node.rule) > 3:
                # remove the key "S-> nn jj kk" from pointers["S"]
                if grammar_node.rule.head.tag in self.heads_pointers and \
                    grammar_node.rule.hash() in self.heads_pointers[grammar_node.rule.head.tag]:
                    self.heads_pointers[grammar_node.rule.head.tag].remove(grammar_node.rule.hash())
                # example:
                # s -> nn jj kk
                # next = nn
                next = grammar_node.rule.head.next
                # temp = jj
                temp = next.next
                # tag = jj-kk
                tag = temp.chain_tags()
                new_rule = RuleNode(tag=tag, next=None, back=next)
                # s -> nn jj-kk
                next.next = new_rule
                # jj-kk -> jj kk
                rule_node = RuleNode(tag=tag, is_head=True, next=temp, back=None)
                rule = Rule(rule_node, is_reconstructed=True)
                new_grammar_rule = GrammarNode(rule, count=1, probability=1.0)
                # jj.back = jj-kk
                temp.back = rule.head

                # {jj-kk->jj kk, s->nn jj-kk}
                # we already changed the rule's next variables, so just copy the count and probability
                stack.append(grammar_node)
                self.heads_pointers[grammar_node.rule.head.tag].add(grammar_node.rule.hash())

                stack.append(new_grammar_rule)
                if new_grammar_rule.rule.head.tag not in self.heads_pointers:
                    self.heads_pointers[new_grammar_rule.rule.head.tag] = set()
                self.heads_pointers[new_grammar_rule.rule.head.tag].add(new_grammar_rule.rule.hash())



            else:
                grammar.update({grammar_node.rule.hash():grammar_node})
                if grammar_node.rule.head.tag not in self.heads_pointers:
                    self.heads_pointers[grammar_node.rule.head.tag] = set()
                self.heads_pointers[grammar_node.rule.head.tag].add(grammar_node.rule.hash())

        self.rules_dictionary = grammar



    def percolate(self, grammar_dictionary):
        stack = list()
        grammar = dict()
        for key, grammar_node in grammar_dictionary.items():
            # S -> VP
            # push all grammar to stack

            stack.append(grammar_node)

        while len(stack) > 0:
            #grammar_node = S->VP
            grammar_node = stack.pop()

            if len(grammar_node.rule) == 2 and not grammar_node.rule.head.next.is_terminal:
                # remove S -> VP
                # ADD S -> populated(VP)
                # search all VP -> XX YY
                # grammar_dictionary[]

                #example:
                # S -> VP
                # VP -> NN PP
                # VP -> A

                # old_key = S->VP
                old_key = grammar_node.rule.hash()

                # probability of S->VP
                p1 = grammar_node.probability

                # remove from pointers of S :  S->VP
                if grammar_node.rule.head.tag in self.heads_pointers and \
                        grammar_node.rule.hash() in self.heads_pointers[grammar_node.rule.head.tag]:
                    self.heads_pointers[grammar_node.rule.head.tag].remove(old_key)

                # percolated_key = VP
                percolated_key = grammar_node.rule.head.next.tag
                # all possible new rules:
                # all_hash_rules_for_percolated_key = ["VP->NN PP"]
                all_hash_rules_for_percolated_key = self.heads_pointers[percolated_key]
                for hash_rule in all_hash_rules_for_percolated_key:
                    # (i=1) Brings VP->NN PP
                    # (i=2) Brings VP->A
                    temp_grammar_node = self.rules_dictionary[hash_rule]
                    p2 = temp_grammar_node.probability
                    # make a new copy of the rule
                    # rule_copy = copy of VP -> NN PP
                    rule_copy = copy.deepcopy(temp_grammar_node.rule)
                    # next = NN
                    next = rule_copy.head.next
                    # new rule_head = S
                    new_rule_head = RuleNode(tag=grammar_node.rule.head.tag,
                                             is_head=True, next=next,
                                             back=None, is_terminal=False)
                    # NN.back = S
                    next.back = new_rule_head
                    # S -> NN PP
                    new_rule = Rule(new_rule_head, is_reconstructed=True)

                    if not new_rule.is_circular() and new_rule.hash() not in grammar_dictionary:
                        # set new grammar rule
                        new_grammar_rule = GrammarNode(new_rule, count=1, probability=p1*p2)

                        # add rules to test percolation
                        # new_grammar_dictionary = {new_grammar_key: new_grammar_rule}
                        self.heads_pointers[new_grammar_rule.rule.head.tag].add(new_grammar_rule.rule.hash())
                        stack.append(new_grammar_rule)

            else:
                grammar.update({grammar_node.rule.hash():grammar_node})
                self.heads_pointers[grammar_node.rule.head.tag].add(grammar_node.rule.hash())

        self.rules_dictionary = grammar

    #def build_tails(self):
    # root : SBAR-yyDOT ==> TOP => NP SBAR YYDOT
    #
    def to_rule_search(self, to_rule):
       # find all X such that X -> to_rule
       li = list()
       for key, gn in self.rules_dictionary.items():
           temp = gn.rule.head.next
           if temp.chain_tags() == to_rule:
               li.append(gn)
       return li




#g = Grammar()
#g.build_grammar_from_tree(Tree().parse_tree(None, a_sentences[0]))
#g.build_grammar_from_tree((Tree().parse_tree(None, a_sentences[1])))
#g.calculate_probabilities()
#g.binarise(g.rules_dictionary)
#g.percolate(g.rules_dictionary)
#print(g)
##class Rules(object):
#    def __init__(self, rules={}):
#        self.rules = rules
#
#    def tree_to_dict(self, node):
#
#        if node is None or node.is_terminal:
#            return
#
#        parent_tag = node.tag
#        children_tags = tuple(child.tag for child in node.children)
#        count = 1
#
#        if self.rules is None:
#            self.rules = dict()
#
#        if parent_tag in self.rules:
#            children = self.rules.get(parent_tag)
#            if children_tags in children:
#                count = children.get(children_tags)
#                count += 1
#            children[children_tags] = count
#        else:
#            self.rules[parent_tag] = {children_tags: count}
#
#        for child in node.children:
#            self.tree_to_dict(child)
#
#        return self.rules
#
#    def calc_rule_probabilities(self, rules):
#        sum = 0
#        for tag in rules:
#            for child_count in tag.values():
#                sum += child_count
#            for child in tag:
#                tag[child] = tag[child] / sum
#            sum = 0
#
#        return rules
#
#    ## make a copy of rules
#    ## hold class var with num of dummy vars
#    def binarise(self, rules):
#        dummy_count = 0
#        updated_rules = {}
#        for parent, children in rules.items():
#            for child in children:
#                new_parent = parent
#                child_len = len(child)
#                if child_len > 2:
#                    probability = rules[parent][child]
#                    for i in range(child_len - 2):
#                        dummy_var = 'dummy_var_'+str(dummy_count)
#                        dummy_count += 1
#                        new_child = tuple((child[i], dummy_var))
#                        if new_parent not in updated_rules:
#                            new_entry = {new_parent: {new_child: probability}}
#                            updated_rules.update(new_entry)
#                        else:
#                            updated_rules[new_parent][new_child] = probability
#                        print(new_parent+':'+'('+child[i] + ',' + dummy_var + ')'+'='+str(probability))
#                        probability = 1
#                        new_parent = dummy_var
#                    new_child = tuple((child[child_len-2], child[child_len-1]))
#                    new_entry = {new_parent: {new_child: probability}}
#                    print(new_parent + ':' + '(' + child[child_len-2] + ',' + child[child_len-1] + ')' + '=' + str(probability))
#                    updated_rules.update(new_entry)
#
#        keys = rules.keys()
#
#        for parent in keys:
#            delete = [key for key in rules[parent] if len(key) > 2]
#            for child in delete:
#                del rules[parent][child]
#
#        rules.update(updated_rules)
#
#        return rules
#
#    def percolate(self, rules):
#        ## if single child not in rules.keys ==> child is a terminal
#        ## if there are non-terminals with terminal names ==> change non terminal to some dummy variable
#        keys = rules.keys()
#        updated_rules = {}
#        delete = []
#        count = 0
#        while True:
#            is_cnf = True
#            for parent in keys:
#                children_keys = rules[parent].keys()
#                for child_key in children_keys:
#                    if len(child_key) == 1 and child_key[0] in rules:
#                        is_cnf = False
#                        probability = rules[parent][child_key]
#                        child_rule = rules[child_key[0]]
#                        child_rule_copy = copy.deepcopy(child_rule)
#                        for rule in child_rule_copy:
#                            child_rule_copy[rule] = child_rule[rule]*probability
#                        if parent not in updated_rules:
#                            new_entry = {parent: child_rule_copy}
#                            updated_rules.update(new_entry)
#                        else:
#                            updated_rules[parent][child_rule[rule]] = probability
#                        delete.append((parent, child_key))
#            if is_cnf is True or count == 3:
#                break
#            for rule in delete:
#                del rules[rule[0]][rule[1]]
#            rules.update(updated_rules)
#            delete.clear()
#            updated_rules.clear()
#            count += 1
#
#        return rules
#
#
#
#
#def parse_sentences():
#    tree_list = []
#    rules = {}
#
#    t = Tree().parse_tree(None, a_sentences[0])
#    rules = Rules(rules).tree_to_dict(t)
#    rules = Rules().binarise(rules)
#    Rules().percolate(rules)
#
#    # for sentence in a_sentences:
#    #     t = Tree().parse_tree(None, sentence)
#    #     tree_list.append(t)
#    #
#    # for tree in tree_list:
#    #     rules = Rules(rules).tree_to_dict(tree)
#    #
#    # new_rules = Rules().binarise(rules)
#
#
#    return rules
#
#all_rules = parse_sentences()
#print("done!")








