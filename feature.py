## feature.py
## Author: Yangfeng Ji
## Date: 08-29-2014
## Time-stamp: <yangfeng 11/06/2014 14:35:59>

from nltk.tokenize import word_tokenize, sent_tokenize
import string

class FeatureGenerator(object):
    def __init__(self, stack, queue, doclen=None):
        """ Initialization of feature generator

        :type stack: list
        :param stack: list of SpanNode instance

        :type queue: list
        :param queue: list of SpanNode instance

        :type doclen: int
        :param doclen: document length wrt EDUs
        """
        # Stack
        if len(stack) >= 2:
            self.stackspan1 = stack[-1] # Top-1st on stack
            self.stackspan2 = stack[-2] # Top-2rd on stack
        elif len(stack) == 1:
            self.stackspan1 = stack[-1]
            self.stackspan2 = None
        else:
            self.stackspan1, self.stackspan2 = None, None
        # Queue
        if len(queue) > 0:
            self.queuespan1 = queue[0] # First in queue
        else:
            self.queuespan1 = None
        # Document length
        self.doclen = doclen


    def features(self):
        """ Main function to generate features

        1, if you add any argument to this function, remember
           to give it a default value
        2, if you add any sub-function for feature generation,
           remember to call the sub-function here
        """
        features = []
        # Status features
        for feat in self.status_features():
            features.append(feat)
        # Structural features
        for feat in self.structural_features():
            features.append(feat)
            # Lexical features
        for feat in self.lexical_features():
            features.append(feat)
        return features
    

    def structural_features(self):
        """ Structural features
        """
        features = []
        if self.stackspan1 is not None:
            # Beginning and End Word of EDU
            stackspan1_ls_token = self.get_ls_token(self.stackspan1.text)
            features.append(('StackSpan1', 'Begin-Word', stackspan1_ls_token[0]))
            features.append(('StackSpan1', 'End-Word', stackspan1_ls_token[-1]))
            # Length of EDU in tokens
            features.append(('StackSpan1', 'Len', len(stackspan1_ls_token)))
            # Beginning POS of EDU
            features.append(('StackSpan1', 'Begin-Tag', self.stackspan1.pos[0]))
            # Ending POS of EDU
            features.append(('StackSpan1', 'End-Tag', self.stackspan1.pos[-1]))
            # Dependency Head Words
            if (len(self.stackspan1.dep) > 0):
                for head_word in self.stackspan1.dep:
                    features.append(('StackSpan1', 'Head-Words', head_word))
            # Span Length wrt EDUs
            features.append(('StackSpan1','Length-EDU',self.stackspan1.eduspan[1]-self.stackspan1.eduspan[0]+1))
            # Distance to the beginning of the document wrt EDUs
            features.append(('StackSpan1','Distance-To-Begin',self.stackspan1.eduspan[0]))
            # Distance to the end of the document wrt EDUs
            if self.doclen is not None:
                features.append(('StackSpan1','Distance-To-End',self.doclen-self.stackspan1.eduspan[1]))
                
        if self.stackspan2 is not None:
            # Beginning and End Word of EDU
            stackspan2_ls_token = self.get_ls_token(self.stackspan2.text)
            features.append(('StackSpan2', 'Begin-Word', stackspan2_ls_token[0]))
            features.append(('StackSpan2', 'End-Word', stackspan2_ls_token[-1]))
            # Length of EDU in tokens
            features.append(('StackSpan2', 'Len', len(stackspan2_ls_token)))
            # Distance between EDUs
            if self.stackspan1 is not None:
                features.append(('StackSpan2-StackSpan1','EDU-Dist',self.stackspan1.eduspan[0] - self.stackspan2.eduspan[1]))
            # Beginning POS of EDU 
            features.append(('StackSpan2', 'Begin-Tag', self.stackspan2.pos[0]))
            # Ending POS of EDU
            features.append(('StackSpan2', 'End-Tag', self.stackspan2.pos[-1]))
            # Dependency Head Words
            if (len(self.stackspan2.dep) > 0):
                for head_word in self.stackspan2.dep:
                    features.append(('StackSpan2', 'Head-Words', head_word))
            features.append(('StackSpan2','Length-EDU',self.stackspan2.eduspan[1]-self.stackspan2.eduspan[0]+1))
            features.append(('StackSpan2','Distance-To-Begin',self.stackspan2.eduspan[0]))
            if self.doclen is not None:
                features.append(('StackSpan2','Distance-To-End',self.doclen-self.stackspan2.eduspan[1]))
        
        if self.queuespan1 is not None:
            # Beginning and End Word of EDU
            queuespan1_ls_token = self.get_ls_token(self.queuespan1.text)
            features.append(('QueueSpan1', 'Begin-Word', queuespan1_ls_token[0]))
            features.append(('QueueSpan1', 'End-Word', queuespan1_ls_token[-1]))
            # Length of EDU in tokens
            features.append(('QueueSpan1', 'Len', len(queuespan1_ls_token)))
            # Beginning POS of EDU
            features.append(('QueueSpan1', 'Begin-Tag', self.queuespan1.pos[0]))
            # Ending POS of EDU
            features.append(('QueueSpan1', 'End-Tag', self.queuespan1.pos[-1]))
            # Dependency Head Words
            if (len(self.queuespan1.dep) > 0):
                for head_word in self.queuespan1.dep:
                    features.append(('QueueSpan1', 'Head-Words', head_word))
            # Distance between EDUs
            if self.stackspan1 is not None:
                features.append(('QueueSpan1-StackSpan1','EDU-Dist',self.queuespan1.eduspan[0] - self.stackspan1.eduspan[1] ))  #a
            if self.doclen is not None:
                features.append(('QueueSpan1','Distance-To-End',self.doclen-self.queuespan1.eduspan[1]))
            features.append(('QueueSpan1','Distance-To-Begin',self.queuespan1.eduspan[0]))

        # Should include some features about the nucleus EDU
        for feat in features:
            yield feat
        

    def status_features(self):
        """ Features related to stack/queue status
        """
        features = []
        if (self.stackspan1 is None) and (self.stackspan2 is None):
            features.append(('Empty-Stack'))
        elif (self.stackspan1 is not None) and (self.stackspan2 is None):
            features.append(('One-Elem-Stack'))
        elif (self.stackspan1 is not None) and (self.stackspan2 is not None):
            features.append(('More-Elem-Stack'))
        else:
            raise ValueError("Unrecognized status in stack")
        if self.queuespan1 is None:
            features.append(('Empty-Queue'))
        else:
            features.append(('NonEmpty-Queue'))
        for feat in features:
            yield feat


    def lexical_features(self):
        """ Lexical features
        """
        features = []
        # Add the first token from the top-1st span on stack

        for feat in features:
            yield feat
            

    def get_ls_token(self, text):
        """ returns a list of tokens from a text
        """
        text = text.replace('<p>','')                     # removing ending markup
        text = text.translate(None, string.punctuation)   # removing punctuation
        ls_text = word_tokenize(text)                     # tokenize words
        return ls_text

