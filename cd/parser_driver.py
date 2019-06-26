import os.path as path
from os import remove
import time 

def drive(parser_class_under_test, output_treebank_file='output/predicted.txt'):
    ''' a simplified version of the solution driver to be used for testing all submissions '''
    
    parser = parser_class_under_test()
    
    # invoke the training
    before = time.time()
    parser.train()
    print(f'training took {time.time() - before:.1f} seconds')
    
    if path.exists(output_treebank_file):
        remove(output_treebank_file)
    
    # parse
    before = time.time()
    parser.write_parse(
        [['I', 'am', 'the', 'first', 'sentence', 'to', 'parse'],
         ['I', 'am', 'another', 'sentence', 'to', 'parse'],
         ['I', 'am', 'the', 'last', 'sentence', 'to', 'parse']],
        output_treebank_file)
    print(f'parsing took {time.time() - before:.1f} seconds')
    
    # you can use other output paths for your experiments,
    # but for the final submission, you must to use the
    # default one used here:                    
    assert path.exists(output_treebank_file), 'your write_parse method did not write its output!' 
    
    print('thanks for the parsing!\n')
    