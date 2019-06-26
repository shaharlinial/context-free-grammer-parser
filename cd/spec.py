''' 
A class spec to inherit for your submission for each of the programming tasks of this Maman.
The contrived example implementation (solution13.py) exemplifies inheriting this class but
no more than that.
'''

class Spec:
        
    def train(self, training_treebank_file='data/heb-ctrees.train'):
        ''' 
        Function training a parser from a training set of a treebank
         
        Input Argument: file path of a treebank training set file
            
        Returns: None 
        '''
    
    def write_parse(self, sentences, output_treebank_file='output/predicted.txt'):
        ''' 
        Function parsing sentences received as input. The function is expected to write
        its parsed output in the same format as the input treebank. It should write its
        parses into the specified output file, in the same order as the input sentences 
        (because any evaluation will compare this output file to a gold parses file, line by line).
         
        Input Arguments:
        1) a list of lists of strings. each list representing an input sentence to parse.
        2) file path of the output file that this function should write
            
        Returns: None
        '''
                