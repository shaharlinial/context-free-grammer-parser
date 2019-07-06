import time
import copy

class AnnotatedNode(object):
    def __init__(self, tag, parent, annotated_tag, span=None, is_terminal=False, is_binarised=False):
        self.tag = tag
        self.children = []
        self.parent = parent
        self.annotated_tag = annotated_tag
        self.span = span
        self.is_terminal = is_terminal
        self.is_binarised = is_binarised

    def add_children(self, node):
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

    def print_tree(self, treeNode):
        children_tree = ""
        if len(treeNode.children) != 0:
            for child in treeNode.children:
                children_tree += self.print_tree(child)

        if len(children_tree) > 0:
            return "("+treeNode.tag+" "+children_tree+") "
        else:
            return treeNode.tag

    def parse_tree_with_parent_annotation(self, parent, bracket_sentence):

        if parent is not None and parent.is_terminal:
            return

        tag = self.parse_string_sequence(bracket_sentence[1:], " ")
        node = AnnotatedNode(tag=tag, parent=parent, annotated_tag=parent.tag+"^"+tag, is_terminal=False)
        if self.tree is None:
            self.tree = node

        if parent is None:
            start_span = 0
        else:
            if len(parent.children) == 0:
                start_span = parent.span[0]
            else:
                start_span = parent.children[-1].span[1]

        node.span = (start_span, start_span + 1)

        if bracket_sentence.count('(') == 1 and bracket_sentence.count(')') == 1:
            tag = self.parse_string_reverse_sequence(bracket_sentence[:-1], " ")
            n_node = AnnotatedNode(tag=tag, parent=node, annotated_tag=tag, span=node.span, is_terminal=True)
            node.add_children(n_node)
            return node

        idx = 0
        to_idx = 0
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

        node.span = (start_span, node.children[-1].span[1])

        return node

    # TODO: build grammar from annotated parent tree. For example:
    # NP ^ S → Det ^ NP   Noun ^ NP
    # NP ^ S → Pro ^ NP
    # NP ^ VP → Det ^ NP   Noun ^ NP
    # NP ^ S → Pro ^ NP

    def build_tree_from_cky_root_node(self, ckynode, parent=None):

        if ckynode.left_child is None and ckynode.right_child is None:
            # Todo: could is_terminal be false here?
            return AnnotatedNode(tag=ckynode.tag, parent=parent, is_terminal=True)

        # if parent is None and not ckynode.tag == "TOP":
        #     top_parent = Node(tag="TOP", parent=None, span=ckynode.span)
        #     self.tree = top_parent
        #     s_parent = Node(tag="S", parent=top_parent, span=ckynode.span)
        #     parent = s_parent
        #     top_parent.add_children(parent)

        # if not ckynode.grammar_rule.rule.is_binarised:
        #     parent = Node(ckynode.tag, parent=parent, span=ckynode.span, is_terminal=False)
        # else:
        #     print(ckynode.tag + " is binarised")
        parent = AnnotatedNode(ckynode.tag, parent=parent, span=ckynode.span, is_terminal=False, is_binarised=ckynode.grammar_rule.rule.is_binarised)
        # one time - create root of tree
        if self.tree is None:
            self.tree = parent

        if ckynode.left_child is not None:
            parent.add_children(self.build_tree_from_cky_root_node(ckynode.left_child, parent))
        if ckynode.right_child is not None:
            parent.add_children(self.build_tree_from_cky_root_node(ckynode.right_child, parent))

        return parent

    def de_binarise(self, node=None):
        # TODO: check before automatically adding TOP-S-
        if node is None and self.tree.tag is not "TOP":
            t_node = AnnotatedNode("TOP", None, self.tree.span, False, False)
            s_node = AnnotatedNode("S", t_node, self.tree.span, False, False)
            t_node.add_children(s_node)
            s_node.add_children(self.tree)
            self.tree.parent = s_node
            self.tree = t_node

        if node is None:
            node = self.tree

        if node.children is not None:
            children = node.children

        if node.is_binarised:
            new_parent = node.parent
            if children is not None:
                for child in children:
                    child.parent = new_parent
                new_parent.children.remove(node)
                new_parent.children.extend(children)

        if children is not None:
            for child in children:
                self.de_binarise(child)


    def get_tree_span(self, node=None, span_set=None):
        if span_set is None:
            span_set = set()
        if node is None:
            node = self.tree
        if not node.is_terminal:
            span_set.add((node.span[0], node.tag, node.span[1]))
            if node.children is not None:
                for child in node.children:
                    self.get_tree_span(child, span_set)
        return span_set

class RuleNode(object):
    def __init__(self, tag, is_head=False, next=None, back=None, is_terminal=False):
        self.tag = tag
        self.is_head = is_head
        self.is_terminal = is_terminal
        self.next = next
        self.back = back

    #returns the current tag chained by following tags "s->nn->jj"
    def chain_tags(self):
        chain = self.tag
        temp = self

        while temp.next is not None:
            chain += ('-' + temp.next.tag)
            temp = temp.next
        return chain

    def improved_chain_tags(self):
        chain = self.tag
        temp = self

        while temp.next is not None:
            chain += ('|' + temp.next.tag)
            temp = temp.next
        return chain


class Rule(object):
    def __init__(self, node, is_binarised=False, is_percolated=False):
        self.head = node
        self.is_binarised = is_binarised
        self.is_percolated = is_percolated

    def insert(self, node):
        temp = self.head
        while temp.next is not None:
            temp = temp.next
        new_node = node
        temp.next = new_node
        new_node.back = temp

    def hash(self):
        temp = self.head
        hash_key = temp.annotated_tag + "->"
        while temp.next is not None:
            temp = temp.next
            hash_key += temp.annotated_tag
            if temp.next is not None:
                hash_key += " "
        return hash_key

    # to prevent NP->NP | SBAR->SBAR | A -> B  | B -> C | C -> A
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
        self.unknown_words = dict()

    def build_grammar_from_tree(self, tree_head):
        #process tree... -> self.rule_list = TREE_PROCCESSED
        node = tree_head
        if node is None or node.is_terminal:
            return

        if len(node.children) == 1 and node.children[0].is_terminal:
            rule = Rule(RuleNode(tag=node.tag, is_head=True))
            rule.insert(RuleNode(tag=node.children[0].tag, is_head=False, is_terminal=node.children[0].is_terminal))
        else:
            rule = Rule(RuleNode(tag=node.annotated_tag, is_head=True))
            for children in node.children:
                rule.insert(RuleNode(tag=children.annotated_tag, is_head=False, is_terminal=children.is_terminal))

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
            grammar_rule.probability = grammar_rule.count / self.heads_count[grammar_rule.rule.head.annotated_tag]


    def gen_unknown_word_probability(self):
        self.populate_tails()
        self.pos_probability = dict()

        tot = 0.0
        pos = dict()

        for rule in self.rules_dictionary.values():
            if len(rule.rule) == 2 and rule.rule.head.next.is_terminal:
                tot += 1.0
                if rule.rule.head.tag not in pos:
                    pos[rule.rule.head.tag] = 1.0
                else:
                    pos[rule.rule.head.tag] += 1.0
        l = ['VB','JJ','NNPS','NNP','NN','NNS']

        for pos_tag, count in pos.items():
            if pos_tag in l:
                pos_probability  = count / tot
                unknown_word = RuleNode(tag='#', is_head=False, is_terminal=True, next=None)
                temp_rule = RuleNode(tag=pos_tag, is_head=True, is_terminal=False, back=None, next=unknown_word)
                unknown_word.back = temp_rule
                new_temp_rule = Rule(node=temp_rule, is_binarised=False,is_percolated=False)
                new_grammar_node = GrammarNode(rule=new_temp_rule, probability=pos_probability, count=count)
                self.unknown_words[new_temp_rule.hash()] = new_grammar_node

    def binarise(self):
        # {s -> nn jj kk } PROB: 0.5
        # s->nn JJKK PROB:0.5
        # np-> nn jj kk PROB:0.4
        # np -> nn JJKK PROB: 0.4
        # JJKK -> jj kk PROB: 1
        # s -> NP PROB: 0.3
        # NP -> vp nn PROB: 0.6
        # s-> vp nn 0.3*0.6
        # [Rule,Rule,Rule...]

        stack = list()

        # push to stack rules that require binarisation
        for grammar_node in self.rules_dictionary.values():
            if len(grammar_node.rule) > 3:
                stack.append(grammar_node)

        while len(stack) > 0:
            # {s -> nn jj kk } PROB: 0.5
            # {s -> nn jj kk}
            grammar_node = stack.pop()

            # remove the value "S-> nn jj kk" from pointers["S"]
            if grammar_node.rule.head.tag in self.heads_pointers and \
                grammar_node.rule.hash() in self.heads_pointers[grammar_node.rule.head.tag]:
                self.heads_pointers[grammar_node.rule.head.tag].remove(grammar_node.rule.hash())
            # remove the key "S-> nn jj kk" from rules_dictionary
            if grammar_node.rule.hash() in self.rules_dictionary:
                del self.rules_dictionary[grammar_node.rule.hash()]
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
            grammar_node.rule.is_binarised = True

            # grammar_node is fixed. Add the fixed rule to rules_dictionary and update heads_pointers
            new_dict = {grammar_node.rule.hash(): grammar_node}
            self.rules_dictionary.update(new_dict)
            if grammar_node.rule.head.tag not in self.heads_pointers:
                self.heads_pointers[grammar_node.rule.head.tag] = set()
            self.heads_pointers[grammar_node.rule.head.tag].add(grammar_node.rule.hash())

            # jj-kk -> jj kk
            rule_node = RuleNode(tag=tag, is_head=True, next=temp, back=None)
            rule = Rule(rule_node, is_binarised=True)
            new_grammar_rule = GrammarNode(rule, count=1, probability=1.0)
            # jj.back = jj-kk
            temp.back = rule.head

            # if new_grammar_rule is not in cnf put it in the stack. Otherwise add to rules_dictionary and heads_pointers
            if len(new_grammar_rule.rule) > 3:
                stack.append(new_grammar_rule)
            else:
                new_dict = {new_grammar_rule.rule.hash(): new_grammar_rule}
                self.rules_dictionary.update(new_dict)
                if new_grammar_rule.rule.head.tag not in self.heads_pointers:
                    self.heads_pointers[new_grammar_rule.rule.head.tag] = set()
                self.heads_pointers[new_grammar_rule.rule.head.tag].add(new_grammar_rule.rule.hash())

        # stack is empty, all rules binarised.
        print("Binarise finished")

    def percolate(self):
        t1 = time.time()
        stack = list()
        for grammar_node in self.rules_dictionary.values():
            # S -> VP
            # push rules to perlocate
            if len(grammar_node.rule) == 2 and not grammar_node.rule.head.next.is_terminal and\
                    not grammar_node.rule.head.tag == grammar_node.rule.head.next.tag:
                stack.append(grammar_node)
        i = 0
        while len(stack) > 0:

            #grammar_node = S->VP
            grammar_node = stack.pop()

            # remove S -> VP
            # ADD S -> populated(VP)
            # search all VP -> XX YY

            #example:
            # S -> VP
            # VP -> NN PP
            # VP -> A

            # probability of S->VP
            p1 = grammar_node.probability

            # percolated_key = VP
            percolated_key = grammar_node.rule.head.next.tag
            # all possible new rules:
            # all_hash_rules_for_percolated_key = ["VP->NN PP"]
            all_hash_rules_for_percolated_key = self.heads_pointers[percolated_key]

            rules_to_percolate = list()
            for hash_rule in all_hash_rules_for_percolated_key:
                # (i=1) Brings VP->NN PP
                # (i=2) Brings VP->A
                temp_grammar_node = self.rules_dictionary[hash_rule]

                # if this rule(temp_grammar_node) needs percolation save in list
                # this rule is also in the stack
                if len(temp_grammar_node.rule) == 2 and not temp_grammar_node.rule.head.next.is_terminal:
                    if temp_grammar_node in stack:
                        rules_to_percolate.append(temp_grammar_node)
                        stack.remove(temp_grammar_node)
                else:
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
                    new_rule = Rule(new_rule_head, is_percolated=True)

                    if not new_rule.is_circular() and new_rule.hash() not in self.rules_dictionary:
                        # set new grammar rule
                        new_grammar_rule = GrammarNode(new_rule, count=1, probability=p1 * p2)
                        # new_grammar_dictionary = {new_grammar_key: new_grammar_rule}
                        new_dict = {new_grammar_rule.rule.hash(): new_grammar_rule}
                        self.rules_dictionary.update(new_dict)
                        if new_grammar_rule.rule.head.tag not in self.heads_pointers:
                            self.heads_pointers[new_grammar_rule.rule.head.tag] = set()
                        self.heads_pointers[new_grammar_rule.rule.head.tag].add(new_grammar_rule.rule.hash())

            # we are finished with grammar_node. remove from dictionary and heads
            key = grammar_node.rule.hash()
            if key in self.rules_dictionary:
                del self.rules_dictionary[key]
            if grammar_node.rule.head.tag in self.heads_pointers:
                rule_set = self.heads_pointers[grammar_node.rule.head.tag]
                if key in rule_set:
                    rule_set.remove(key)
            if len(rules_to_percolate) > 0:
                # If rules to percolate not empty push grammar_rule back and push rules_to_percolate on top
                stack.append(grammar_node)
                stack.extend(rules_to_percolate)
                rules_to_percolate.clear()
            i += 1
        # stack is empty, all rules percolated.
        print("Finished percolate in %s" % str(time.time() - t1))

    def populate_tails(self):
        self.tails_pointers = dict()
        for rule_hash, grammar_node in tqdm(self.rules_dictionary.items(), "populating tails..."):
            key = grammar_node.rule.head.next.improved_chain_tags()
            if key not in self.tails_pointers:
                self.tails_pointers[key] = set()
            self.tails_pointers[key].add(rule_hash)

