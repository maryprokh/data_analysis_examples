# Python program - FastAPI app calculator which firstly converts infix notation to postfix notation
#(Inverse Polish Notation) and after that uses stack to calculate the expression

#Before the running, it shouls install all the necessary modules and create fastapi enviroment
#For running, enter in a console the following command: uvicorn fastapi_calculator:app --reload
#The good instruction is given in this video, chapter " (00:10:09) Install and Setup".
#The link: https://www.youtube.com/watch?v=7t2alSnE2-I

#import modules
from fastapi import FastAPI
import re

#additional functions needed for expression processing
#functon that treats floats in the expression
def extract_float(expr):
    pattern1 = r'(\d*\.\d*)'
    r = re.split(pattern1, expr)
    f = []
    for item in r:
      if '.' in item:
        f.append(item)
      else:
        f.extend(re.split(r'(\d+)', item))
    return f  

#function that treats a sign before the first element
def transform_first(listt):
        if listt[0] == '-':
            listt[1] = '-' + listt[1]
            listt.remove(listt[0])
        elif listt[0] == '+':
            listt.remove(listt[0])
        return listt
#function that deletes spaces in the expression
def delete_spaces(string):
    return string.replace(' ', '')

# Class to convert the expression
class Conversion:
    # Constructor to initialize the class variables
    def __init__(self, capacity):
        self.top = -1
        self.capacity = capacity
        # This array is used a stack
        self.array = []
        # Precedence setting: e.g. exponentiation has the highest priority
        self.output = []
        self.precedence = {'+':1, '-':1, '*':2, '/':2, '^':3}
     
    # check if the stack is empty
    def isEmpty(self):
        return True if self.top == -1 else False
     
    # Return the value of the top of the stack
    def peek(self):
        return self.array[-1]
     
    # Pop the element from the stack
    def pop(self):
        if not self.isEmpty():
            self.top -= 1
            return self.array.pop()
        else:
            return "$"
     
    # Push the element to the stack
    def push(self, op):
        self.top += 1
        self.array.append(op)
 
    # A utility function to check is the given character
    # is operand
    def isOperand(self, ch):
      try:
         float(ch)
         return True
      except ValueError:
         return False

    # Check if the precedence of operator is strictly
    # less than top of stack or not
    def notGreater(self, i):
        try:
            a = self.precedence[i]
            b = self.precedence[self.peek()]
            return True if a  <= b else False
        except KeyError:
            return False

    # The main function that
    # converts given infix expression
    # to postfix expression (Reverse Polish Notation)
    def infixToPostfix(self, exp):
        exp = transform_first(extract_float(delete_spaces(exp))) 
        try:
          index1 = [idx for idx, s in enumerate(exp) if '(' in s][0]
          exp[index1] = list(exp[index1])
          exp = exp[:index1] + exp[index1] + exp[index1+1:]
          
          index2 = [idx for idx, s in enumerate(exp) if ')' in s][0]
          exp[index2] = list(exp[index2])
          exp = exp[:index2] + exp[index2] + exp[index2+1:]
        except:
          print('no brackets')

        # Iterate over the expression for conversion
        for i in exp:
            # If the character is an operand,
            # add it to output
            if self.isOperand(i):
                self.output.append(i)
            # If the character is an '(', push it to stack
            elif i  == '(':
                self.push(i)
 
            # If the scanned character is an ')', pop and
            # output from the stack until and '(' is found
            elif i == ')':
                while( (not self.isEmpty()) and
                                self.peek() != '('):
                    a = self.pop()
                    self.output.append(a)
                if (not self.isEmpty() and self.peek() != '('):
                    return -1
                else:
                    self.pop()
 
            # An operator is encountered
            else:
                while(not self.isEmpty() and self.notGreater(i)):
                  self.output.append(self.pop())
  
                self.push(i)
 
        # pop all the operator from the stack
        while not self.isEmpty():
            self.output.append(self.pop())
        return self.output

#function that uses stack for parsing Reverse Polish notation and returns the result
    def calc(self):
      #function checks if an element is a number
      def is_number(arg):
        try:
          float(arg)
          return True
        except ValueError:
          return False 
      #function that rounds the result if it's a float
      def rounded(res):
        if float(res) % 1 == 0.0:
          return int(float(res))
        else:
          return round(float(res),3)    

      try:
        stack = []    
        for item in self.output:
         if is_number(item):
           stack.append(float(item))
         elif item == '*':
           stack.append(stack.pop()* stack.pop())
         elif item == '-':
           stack.append(stack.pop(0)- stack.pop(0))
         elif item == '+':
           stack.append(stack.pop()+ stack.pop())
         elif item == '/':
           stack.append(stack.pop(-2) /stack.pop())
         elif item == '^':
           stack.append(stack.pop(-2) ** stack.pop())
         else:
            if item != '':
              return ''
        list_res = [str(item) for item in stack]
        str_res = "".join(list_res)
        return rounded(str_res)
      except:
        return ''

#Functions to return the result and the history of operations
history_list = []
def return_result(expression):
    obj = Conversion(len(expression))
    converted = obj.infixToPostfix(expression)
    #print(f'result{converted}')
    return str(obj.calc())

def append_data(expression):
    responce = return_result(expression)
    data = {'request': None, 'responce': None, 'status': None}
    data['request'] = expression
    data['responce'] = responce
    if data['responce'] != '':
      data['status'] = 'success'
    else:
      data['status'] = 'fail'
    history_list.append(data)
    return history_list

#Application code    
app = FastAPI()
#app function to get the result
@app.get('/calc')
def calculator(expression):
  append_data(expression)
  return return_result(expression)

@app.get('/history')
#app function to get the history of the results and filter them
#we can show up to 30 operations and filter if they were successful or failed
def history(limit:int = 30, status:str = None):
  if 1<= limit <= 30:
    if status in ('success', 'fail'):
       filtered = filter(lambda diction: diction['status'] == status, history_list)
       return list(filtered)[:limit]
    elif status == None:
       return history_list[:limit]
    else:
       return 'Error.Incorrect status value'
  else:
    return 'Error. Incorrect limit number'
  
