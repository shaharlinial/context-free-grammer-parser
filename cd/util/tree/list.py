class List():
    
    def __init__(self, head):
        self.head = head
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        
    
