import string
import re
START_SYMBOL = '<S>'  

class Converter:
    def __init__(self, regx:str) -> None:
        self.regx=regx
        self.nonTerminal=[]
        self.alphabet=[]
        self.grammar={START_SYMBOL: [""]}
        self.counter=0
        self.specialChar={'*', '|', '(',')'}

        self.convertRegX2Gram()

    #returns list of all alphabets in regex
    def getAlphabets(self)->list:
        if len(self.alphabet)!=0:
            return self.alphabet
        for char in self.regx:
            if char not in self.specialChar and char not in self.alphabet:
                self.alphabet.append(char)  
        return self.alphabet
    
    #returns grammar dictionary
    def getGrammar(self)-> dict:
        return self.grammar
    
    #generates symbol
    #returns alphabets in capital  and in format '<A>'
    def symbolGen(self):
        keys=list(string.ascii_letters.upper())
        symbol=keys[self.counter]
        self.counter+=1
        newsymbol='<'+symbol+'>'
        return newsymbol
    
    def emptyStringGram(self):
        if len(self.regx)==0:
            self.grammar[START_SYMBOL]=""
    
    
    def convertRegX2Gram(self):
        self.grammar[START_SYMBOL]=[]
        self.handleExpression(START_SYMBOL, self.regx)
    

    #returns key for a given value in dictionary or returns None if value does not exist
    def keyFinder(self,value, given_dict):
        for key, val in given_dict.items():
            if value in val:
                return key
        return None  

    #function to handle strings with no symbols    
    def handleNoTerminalExp(self, currentSymbol):
        char=self.getAlphabets()
        self.grammar[currentSymbol]=[] # making an empty list
        keysGenerated=[]
        for c in char:

            #Generate key for each unique alphabet and store its corresponding value
            currentSymbol=self.symbolGen() #Generating a new key
            keysGenerated.append(currentSymbol)
            self.grammar[currentSymbol]=[] #making list as itme to that key
            self.grammar[currentSymbol].append(c) #appending the alphabet as an item to the list 
            #print("Printing Saved grammar")
            #print(self.grammar)
        
        allChar=list(self.regx)
        #print(allChar)
        symbolstr=""
        for c in allChar:
            key=self.keyFinder([c],self.grammar)# remember the item is in a list
            #print(key)
            if key!=None:
                symbolstr+=key
        self.grammar[START_SYMBOL].append(symbolstr)
    

    def handleKleenStar(self, currentSymbol):
        #lets  try for just a*
                
        #Generate a nonterminaSymbol
        self.grammar[currentSymbol]=[]
        newSymbol=self.symbolGen()
        self.grammar[currentSymbol].append(newSymbol) #points to the key of next dict item
        currentSymbol=newSymbol
        self.grammar[currentSymbol]=[]
        #self.grammar[currentSymbol].append


        for index, character in enumerate(self.regx):
            if character!='*':
                #newSymbol=self.symbolGen()
                self.grammar[currentSymbol].append(character+currentSymbol)
                #currentSymbol=newSymbol
                #self.grammar[currentSymbol]=[]
            
            else:
                newStr=self.grammar[currentSymbol][0]
                newStr=newStr+'|'+""
                self.grammar[currentSymbol]=[newStr]
        #self.grammar[currentSymbol].append("")        


    def handleEithersymbol(self, currentSymbol):
        characters=self.regx.split('|')
        newSymbol=""
        for c in characters:
            newSymbol=self.symbolGen()
            self.grammar[currentSymbol].append(newSymbol)
            #print(self.grammar)
            self.grammar[newSymbol]=[]
            self.grammar[newSymbol].append(c)

        currentSymbol=newSymbol
        return currentSymbol
    
    def handleJustChar(self, char, currentSymbol):
        checkExist=self.keyFinder(char, self.grammar) #check if a value exist
        if checkExist!=None: # if not we add that to the existing 
            val=self.grammar[START_SYMBOL]#[0]   # returns a list
            #print("Val details11")
            #print(type(val))
            val[0]+=checkExist  #add the existing character key to the first key item
            self.grammar[START_SYMBOL]=val
            
        elif checkExist==None:
            newSymbol=self.symbolGen()
            val=self.grammar[START_SYMBOL]   # returns a list
            #print("Val details")
            #print(len(val))
            if len(val)==0:  #just adding the key of the new character in the value of the first key
                val.append(newSymbol)
            else:
                val[0]+=newSymbol
        
            #print(val)

            self.grammar[newSymbol]=[]
            self.grammar[newSymbol].append(char)
            currentSymbol=newSymbol

        return currentSymbol

    def handleEither(self,givenStrLst, index ,currentSymbol):
        #self.grammar[START_SYMBOL][0]+='|'
        k=self.keyFinder(givenStrLst[index+1], self.grammar)
        if k==None:
            newKey=self.symbolGen()
            self.grammar[START_SYMBOL].append(newKey)
            self.grammar[newKey]=[]
            self.grammar[newKey].append(givenStrLst[index+1])
            #print(givenStrLst[index+1])
        else:
            self.grammar[START_SYMBOL].append(k)

        
        
              

    def handleKleenStar(self, index, characterList: list):
        #get th key of the previous character before *
        # access the key value pair (value is the list)
        #in the list, concatinate the keythe the existing item in the list/ lowercase alphabet
        #concatinate the | "" to it
        previousChar=characterList[index-1] #getting th eprevious character
        #print("the prevChar is: "+ previousChar)
        prevCharKey=self.keyFinder(previousChar, self.grammar) #getting the key of that character
        #print("Previous char is: "+ previousChar+ " key: "+prevCharKey)

        value=self.grammar[prevCharKey]
        value=value[0]    #we now have what is already stored in that key
        value=value+prevCharKey
        self.grammar[prevCharKey]=[value]
        self.grammar[prevCharKey].append("")

        pass
    
    
    #might have to change fucntoion for nested parenthesis
    def extractStrBtwParentheses(self,inputStr: str, index: int):
        matches = re.findall(r'\((.*?)\)', inputStr)
        if index - 1 < len(matches):
            return matches[index - 1]
        else:
            return None

    def handleParenthesisStar(self):
        
        newKey=self.symbolGen()
        newDict={newKey: []}
        newDict[newKey].append(START_SYMBOL+newKey)
        newDict[newKey].append("")
        self.grammar= {**newDict, **self.grammar }
        key1=newKey
        key2=START_SYMBOL
        new_dict = {key2 if k == key1 else key1 if k == key2 else k: v for k, v in self.grammar.items()}
        self.grammar=new_dict


    def handleDupKey(self, gram: dict):
        seenValues = {}
        keysToDelete = []
        trackingDict = {}

        for key, value in gram.items():
            value_tuple = tuple(value) if isinstance(value, list) else value
            if value_tuple in seenValues:
                keysToDelete.append(key)
                if seenValues[value_tuple] in trackingDict:
                    trackingDict[seenValues[value_tuple]].append(key)
                else:
                    trackingDict[seenValues[value_tuple]] = [key]
            else:
                seenValues[value_tuple] = key

        for key in keysToDelete:
            del gram[key]

        #self.grammar=gram
        print("TRYYYY")
        print(gram)
        print(trackingDict)
        return trackingDict



    
    def handleExpression(self,currentSymbol, regexStr: str):

        #currentSymbol=START_SYMBOL
        

        all_char=list(regexStr)
        #print(all_char)
        
        index=0
        parenthesis_index=1

        while index< len(all_char):
            characters=all_char[index]
            # print(self.grammar)
            #print("Character in for loop is: "+ characters+ "  index is "+ str(index))
            #print("THis is current character "+characters)
            if characters =='(':
                parenthesisStr=self.extractStrBtwParentheses(regexStr, parenthesis_index)  #extracting string between parenthesis
                # print("THIS IS PARENTHESIS")
                # print(parenthesisStr)
                parenthesis_index+=1
                if parenthesisStr!=None:
                    self.handleExpression(currentSymbol,parenthesisStr)
                    # print("THIS is GRAMMAR")
                    # print(self.grammar)
                if (index+len(parenthesisStr)+2)<len(all_char):    
                    if parenthesisStr!=None and all_char[index+len(parenthesisStr)+2]=='*': #checking if the next character is * after )
                        
                        self.handleParenthesisStar()
                        index=index+len(parenthesisStr)+3
                        continue
                    
                index=index+len(parenthesisStr)+2
                continue
                        
                pass
            elif characters == '*':
                #index= all_char.index(characters) #index of the character that is *
                #print("PREVCharacter in for loop is: "+ all_char[index-1])

                self.handleKleenStar(index,all_char)
                #pass
            elif characters == '|':
                self.handleEither(all_char, index,currentSymbol)
                index+=1
            elif '|' or '(' or ')' or '*'  or "" not in characters:
                currentSymbol=self.handleJustChar(characters, currentSymbol)

            index+=1
        #self.handleDupKey(self.grammar)

        return
