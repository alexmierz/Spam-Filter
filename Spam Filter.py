
############################################################
# Imports
############################################################
import math
import email
import os

from collections import OrderedDict

############################################################
# Section 1: Spam Filter
############################################################

def load_tokens(email_path):
    #use .split()
    messagelist = []
    
    file = open(email_path, "r")
    
    message = email.message_from_file(file)
    
    iteration = email.iterators.body_line_iterator(message)

    for x in iteration:
        if messagelist == 0:
            return False
        
        else:
            messagelist =  messagelist + x.split()

    return messagelist


def log_probs(email_paths, smoothing):
    
    word = {}
    sameWord = set()
    vocabCount = 0
    
    result = {}
    total = 0
    
    for x in email_paths:

        allTokens=load_tokens(x)
        length = len(allTokens)
        
        for x in range(length):
            alltokens = tuple(allTokens[x])
            
            if alltokens in sameWord:
                word[allTokens[x]] = (word[allTokens[x]] + 1)
                
            else:
                word[allTokens[x]] = 1
                vocabCount = vocabCount + 1
                sameWord.add(tuple(allTokens[x]))
         
    for x in word:
        total = total + word[x]
        totalres = (total + smoothing * (vocabCount + 1))
        
    result["<UNK>"] = (math.log(smoothing / totalres))

    #check if word exists in file
    for x in word:
        if total == 0:
            return False
        
        elif total < 0:
            return False
        #final case return final result with math to find correct result
        else:
            result[x] = (math.log((word[x] + smoothing) / (totalres)))
        
    return result


class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):
        self.spam_dir = spam_dir
        self.ham_dir = ham_dir
        self.smoothing = smoothing
        
        self.unloggedHam = {}
        self.unloggedSpam = {}
        
        spam = []
        ham = []
        
        for x in os.listdir(spam_dir):
            if spam_dir == 0:
                return False
            
            else:
                name = os.fsdecode(x)
                output1 = "/" + name
                
                append1 = spam_dir + output1
                spam.append(append1)
            
        for x in os.listdir(ham_dir):
            if ham_dir == 0:
                return False
            
            else: 
                name = os.fsdecode(x)
                output2 = "/" + name
            
                append2 = (ham_dir + output2)
                ham.append(append2)    
        
        self.probHam = math.log(len(ham) / (len(spam) + len(ham)))
        self.probSpam = math.log(len(spam) / (len(spam) + len(ham)))
    
        self.hamDict = log_probs(ham,smoothing)
        self.spamDict = log_probs(spam,smoothing)
        
        
        for x in self.hamDict:
            self.unloggedHam[x] = math.exp(self.hamDict[x])
            
        for x in self.spamDict:
            self.unloggedSpam[x] = math.exp(self.spamDict[x])
        
        splitspam = self.unloggedSpam.keys()
        
        listSpam = " ".join(splitspam).split()
        
        splitham = self.unloggedHam.keys()
        
        listHam = " ".join(splitham).split()
        
        self.unionSet = set().union(listHam, listSpam)


        
    def isSpamHelperFunc(self, directory):
        
        vocabCount = 0
        word = {}
        sameWord = set()
    
        
        oneEmailTokens = load_tokens(directory)
        
        length = len(oneEmailTokens)
        
        for x in range(length):
            if tuple(oneEmailTokens[x]) not in sameWord:
                
                word[oneEmailTokens[x]] = 1
                
                vocabCount = vocabCount + 1
                
                sameWord.add(tuple(oneEmailTokens[x]))
                
            else:
                word[oneEmailTokens[x]] = (word[oneEmailTokens[x]] + 1)
                
        return word
        
    
    def is_spam(self, email_path):
        #initalize currentword variable to keep track
        currentWord = self.isSpamHelperFunc(email_path)
        
        #initalize spam and ham
        probablyHam = self.probHam
        probablySpam = self.probSpam
        
        
        #Tokens which were not encountered during the training process should be converted into
        #the special word "<UNK>" in order to avoid zero probabilities.
        
        #checking is HAM
        for x in currentWord:
            current = currentWord[x]
            if x in self.hamDict:
                probablyHam = (probablyHam + self.hamDict[x] * current)
                
            elif x in self.hamDict and self.spamDict:
                return False
            
            else:
                probablyHam = (probablyHam + self.hamDict["<UNK>"] * current)
                
        #checking if SPAM    
        for x in currentWord:
            current = currentWord[x]
            if x in self.spamDict:
                probablySpam = (probablySpam + self.spamDict[x] * current)
                
            elif x in self.spamDict and self.hamDict:
                return False
            
            else:
                probablySpam = (probablySpam + self.spamDict["<UNK>"] * current)
                
        if probablyHam == probablySpam:
            return False
      
        elif probablyHam <= probablySpam:
            return True
        
        elif probablyHam >= probablySpam:
            return False 
        
        else:
            return False

    def most_indicative_spam(self, n):
        
        count = 0
        unionset = self.unionSet
        result = {}
       
        for x in unionset:
            if x in self.hamDict and x in self.spamDict:
                
                result[x] = math.log(self.unloggedSpam[x] / self.unloggedHam[x] + self.unloggedSpam[x])
                
            elif not x in self.hamDict and not x in self.spamDict:
                return False
    
                
        sort = sorted(result.items(), key = lambda x: x[1], reverse = True)
        
        result = []
        resultfinal = OrderedDict(sort)
     
        
        for x in resultfinal:
            if count == n:
                return result
            
            if count > n:
                return False
            
            else:
                result.append(x)
                count = count + 1
