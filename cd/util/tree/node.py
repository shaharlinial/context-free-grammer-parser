from util.tree.util import flatten

class Node():
    
    def __init__(self, tag):
        self.tag = tag
        self.children = []
        #print(f'node created with tag {tag}')
    
    def add_child(self, child):
        self.children.append(child)
    
    def get_downward_arcs(self):
        return self._get_arcs()
        
    def _get_arcs(self):
        arcs = []
        for child in self.children:
            arc = (self.tag, child.tag)
            arcs.append(arc)
            arcs.extend(child._get_arcs())

        return arcs
            
        
        