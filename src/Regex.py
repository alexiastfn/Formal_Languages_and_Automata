from .NFA import NFA
import re
EPSILON = ''
weird_characters = {'_', '.', '@', ':'}
operators = {'*', '+', '?', '|', '#', '['}
get_precedences = {'*': 3, '+': 3, '?': 3, '[': 3, '#': 2, '|': 1}

class Regex:

    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')


def simple_character(element, anterior, posterior):         # verific daca '-' este un caract normal sau face parte din syntathic sugar
    if element == '-':
        if anterior not in {'0', 'a', 'A'} and posterior not in {'9', 'z', 'Z'}:
            return True
        else:
            return False

def get_the_parentheses(expression):        # cauta prima pereche de () si returneaza ce este intre ele
    expression_string = ''.join(expression)
    opening_index = -1
    aux = []

    for index, char in enumerate(expression_string):
        if char == '(':
            if not aux:
                opening_index = index
            aux.append(char)
    if opening_index != -1:
        return expression_string[opening_index + 1:]
    else:
        return None

def search_in_parentheses(expression):      # numarul de operatori in regex
    ops = {'#', '|'}
    counter = 0
    new_expression = get_the_parentheses(expression)
    for char in new_expression:
        if char in ops:
            counter += 1
    return counter

def insert_concatenation_symbols(expression):
    result = []
    #expression = re.sub(r'(?<!\\)\s', '', expression)
    expression = re.sub(r'(?<!\\)(?<!\\n)(\s)', '', expression)

    for i, char in enumerate(expression):
        result.append(char)
        if char.isalnum() or char in weird_characters or char == '-' or char == ')' or char == '\\' or char == ' ':

            if i + 1 < len(expression):
                next_char = expression[i + 1]

                if next_char == '\\':
                    result.append('#')
                    continue


                # if i > 1:
                #     last_char = expression[i - 1]
                #     if last_char == '\\':
                #         result.append('#')
                #         continue


                if char == '-':
                    if i >= 1:
                        anterior = expression[i - 1]
                    if i + 1 < len(expression):
                        posterior = expression[i + 1]
                    temp1 = simple_character('-', anterior, posterior)
                else:
                    temp1 = False

                if next_char == '-':
                    anterior = expression[i]
                    if i + 2 < len(expression):
                        posterior = expression[i + 2]
                    temp2 = simple_character('-', anterior, posterior)
                else:
                    temp2 = False

                if char.isalnum() or char in weird_characters or char == ')' or (char == '-' and temp1 == True) or char == ' ':
                    if next_char.isalnum() or next_char in weird_characters or next_char == '(' or char == '\\' or  (next_char == '-' and temp2 == True) or next_char == ' ' or next_char == '[':
                        result.append('#')

        elif char in {'*', '+', '?'}:
            if i + 1 < len(expression):
                next_char = expression[i+1]
                if next_char.isalnum() or next_char in weird_characters or next_char == '(' or next_char == '\\':
                    result.append('#')

        elif char == ']':
            if i + 1 < len(expression):
                if expression[i + 1] == '[':
                    result.append('#')

        elif i > 1:
            last_char = expression[i - 1]
            if last_char == '\\':
                result.append('#')
                continue

        # verify if char is the last element of the ():
        if i + 1 < len(expression):
            next_char = expression[i + 1]
            if next_char == ')' and search_in_parentheses(result) == 0 and len(expression) > 6:
                result.append('#')

    return result

def helper(op, stack, postfix):     # helper pt stiva, pt a respecta ordinea operatorilor

    while stack and stack[-1] != '(' and get_precedences.get(stack[-1], 0) >= get_precedences.get(op, 0):
        postfix.append(stack.pop())
    stack.append(op)

def new_line_case(i, char, expression):     # pentru testul de '\n'

    if char == 'n' and i >= 1 and expression[i - 1] == '\\':
        return True
    else:
        return False

def postfix(concatenated_expression):   # reverse polish notation
    expression = insert_concatenation_symbols(concatenated_expression)
    stack = []
    postfix = []

    for i, char in enumerate(expression):

        if char == '-':
            if i >= 1:
                anterior = expression[i - 1]
            if i + 1 < len(expression):
                posterior = expression[i + 1]
            temp = simple_character('-', anterior, posterior)
        else:
            temp = False

        if (char.isalnum() and new_line_case(i, char, expression) == False) or char in weird_characters or (char == '-' and temp == True):
            postfix.append(char)
        elif i >= 1 and expression[i - 1] == '\\':
            if char in operators or new_line_case(i, char, expression):
                postfix.append('\\' + char)
            else:
                postfix.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':    # se extrag elemente din stiva si se adaugă in rezultatul postfix pana cand se intalneste o paranteza deschisa
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        elif char in operators:
            helper(char, stack, postfix)

    while stack:    # dupa procesarea tuturor => elem ramase se adauga in forma postifata
        postfix.append(stack.pop())

    return postfix

def parse_regex(regex: str) -> Regex:

    new_regex = postfix(regex)
    for_regex = new_regex.copy()
    stack = []
    global_counter = 0

    for elem in for_regex:
        if len (for_regex) == 1:
            nfa = Character(elem, 0)
            stack.append(nfa)
        elif not elem in operators:
            stack.append(elem)
            new_regex.remove(elem)
        elif elem in operators:
            new_regex.remove(elem)
            if len(for_regex) > 3:
                global_counter += 1

            if elem == '#':
                nfas = []
                if len(stack) < 2:
                    continue
                pop1 = stack.pop()  # b
                pop2 = stack.pop()  # a
                pops_list = []
                pops_list.append(pop2)
                pops_list.append(pop1)

                if isinstance(pop1, NFA) and not isinstance(pop2, NFA):
                    concat_counter = max(pop1.K) + 1
                    nfa = Character(pop2, concat_counter).thompson()
                    global_counter += 2
                    nfas.append(nfa)
                    nfas.append(pop1)
                elif isinstance(pop2, NFA) and not isinstance(pop1, NFA):
                    concat_counter = max(pop2.K) + 1
                    nfa = Character(pop1, concat_counter).thompson()
                    global_counter += 2
                    nfas.append(pop2)
                    nfas.append(nfa)
                elif not isinstance(pop1, NFA) and not isinstance(pop2, NFA):
                    nfas.append(Character(pop2, global_counter).thompson())
                    global_counter += 2
                    nfas.append(Character(pop1, global_counter).thompson())
                    global_counter += 1
                elif isinstance(pop2, NFA) and isinstance(pop1, NFA):
                    nfas.append(pop2)
                    nfas.append(pop1)

                if len(for_regex) <= 3 or len(new_regex) == 0 :
                    nfa = Concat(nfas[0], nfas[1])
                else:
                    nfa = Concat(nfas[0], nfas[1]).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)

            elif elem == '|':
                nfas = []
                if len(stack) < 2:
                    continue
                pop1 = stack.pop()  # b
                pop2 = stack.pop()  # a
                pops_list = []
                pops_list.append(pop2)
                pops_list.append(pop1)

                if isinstance(pop1, NFA) and not isinstance(pop2, NFA):
                    concat_counter = max(pop1.K) + 1
                    nfa = Character(pop2, concat_counter).thompson()
                    nfas.append(nfa)
                    nfas.append(pop1)
                elif isinstance(pop2, NFA) and not isinstance(pop1, NFA):
                    concat_counter = max(pop2.K) + 1
                    nfa = Character(pop1, concat_counter).thompson()
                    nfas.append(pop2)
                    nfas.append(nfa)
                elif not isinstance(pop1, NFA) and not isinstance(pop2, NFA):
                    nfas.append(Character(pop2, global_counter).thompson())
                    nfas.append(Character(pop1, global_counter).thompson())
                elif isinstance(pop2, NFA) and isinstance(pop1, NFA):
                    nfas.append(pop2)
                    nfas.append(pop1)

                if len(for_regex) <= 3 or len(new_regex) == 0 :
                    nfa = Union(nfas[0], nfas[1])
                else:
                    nfa = Union(nfas[0], nfas[1]).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)

            elif elem == "*":
                pop = stack.pop()

                if not isinstance(pop, NFA):
                    nfa = Character(pop, global_counter).thompson()
                    global_counter += 2
                else:
                    nfa = pop

                if len(for_regex) <= 3 or (len(new_regex) <= 1 and len(stack) <= 0):
                    nfa = KleenStar(nfa)
                else:
                    nfa = KleenStar(nfa).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)

            elif elem == '?':
                pop = stack.pop()

                if not isinstance(pop, NFA):
                    nfa = Character(pop, global_counter).thompson()
                    global_counter += 2
                else:
                    nfa = pop

                if len(for_regex) <= 3 or (len(new_regex) <= 1 and len(stack) <= 0):
                    nfa = QuestionMark(nfa)
                else:
                    nfa = QuestionMark(nfa).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)

            elif elem == '+':
                pop = stack.pop()
                global_counter += 1

                if not isinstance(pop, NFA):
                    nfa = Character(pop, global_counter).thompson()
                    global_counter += 2
                else:
                    nfa = pop

                if len(for_regex) <= 3 or (len(new_regex) <= 1 and len(stack) <= 0):
                    nfa = PlusMark(nfa)
                else:
                    nfa = PlusMark(nfa).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)

            elif elem == '[':

                pop = stack.pop()
                stack.pop()
                symbols = []

                if pop == '9':
                    symbols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                elif pop == 'z':
                    symbols = [chr(symbol) for symbol in range(ord('a'), ord('z') + 1)]
                elif pop == 'Z':
                    symbols = [chr(symbol) for symbol in range(ord('A'), ord('Z') + 1)]

                if len(new_regex) < 1:
                    nfa = Character(symbols, global_counter)
                else:
                    nfa = Character(symbols, global_counter).thompson()
                    global_counter = max(nfa.K)
                stack.append(nfa)


    nfa = stack.pop()
    return nfa

class Character(Regex):
    def __init__(self, char, global_counter):
        self.char = char
        self.global_counter = global_counter

    def thompson(self) -> NFA[int]:

            k_nfa_copy = {0, 1}
            k_nfa = set()
            f_nfa = set()
            symbols_nfa = set(self.char)
            # if self.char[0] == '\\':
            #     symbols_nfa = {self.char}
            # if self.char == '\\n':
            #     symbols_nfa = {'\n'}

            transitions_nfa = {}
            if self.global_counter != 0:
                for elem in k_nfa_copy:
                    k_nfa.add(elem + self.global_counter)
            else:
                k_nfa = k_nfa_copy

            q0_nfa = self.global_counter
            f_nfa.add(1 + self.global_counter)

            if len(self.char) != 1:
                for ch in self.char:
                    transitions_nfa[(q0_nfa, str(ch))] = f_nfa
            else:
                transitions_nfa[(q0_nfa, self.char)] = f_nfa

            return NFA(symbols_nfa, k_nfa, q0_nfa, transitions_nfa, f_nfa)



class Concat(Regex):
    def __init__(self, left_nfa: NFA, right_nfa: NFA):
        self.left_nfa = left_nfa
        self.right_nfa = right_nfa

    def thompson(self) -> NFA[int]:

        symbols_nfa = self.left_nfa.S.union(self.right_nfa.S)

        k_nfa = self.left_nfa.K
        k_nfa = k_nfa.union(self.right_nfa.K)

        q0_nfa = self.left_nfa.q0
        f_nfa = self.right_nfa.F

        transitions_nfa = self.left_nfa.d
        transitions_nfa.update(self.right_nfa.d)
        f = self.left_nfa.F.copy()
        transitions_nfa[(f.pop(), EPSILON)] = {self.right_nfa.q0}

        return NFA(symbols_nfa, k_nfa, q0_nfa, transitions_nfa, f_nfa)

class Union(Regex):
    def __init__(self, first_nfa: NFA, second_nfa: NFA):
        self.first_nfa = first_nfa
        self.second_nfa = second_nfa

    def thompson(self) -> NFA[int]:

        symbols_nfa = self.first_nfa.S.union(self.second_nfa.S)
        k_nfa_copy = self.first_nfa.K
        k_nfa_copy = k_nfa_copy.union(self.second_nfa.K)
        k_nfa = k_nfa_copy

        q0_nfa = max(max(self.first_nfa.K), max(self.second_nfa.K)) + 1
        f_nfa = set()
        f_nfa.add(q0_nfa + 1)

        transitions_nfa = self.first_nfa.d
        transitions_nfa.update(self.second_nfa.d)
        transitions_nfa[(q0_nfa, EPSILON)] = {self.first_nfa.q0, self.second_nfa.q0}
        f1 = self.first_nfa.F.copy()
        k1 = f1.pop()
        f2 = self.second_nfa.F.copy()
        k2 = f2.pop()
        transitions_nfa[(k1, EPSILON)] = f_nfa
        transitions_nfa[(k2, EPSILON)] = f_nfa

        k_nfa = k_nfa.union({q0_nfa})
        k_nfa = k_nfa.union(f_nfa)
        k_nfa = k_nfa.union({self.first_nfa.q0, self.second_nfa.q0})

        return NFA(symbols_nfa, k_nfa, q0_nfa, transitions_nfa, f_nfa)


class KleenStar(Regex):
    def __init__(self, current_nfa: NFA):
        self.current_nfa = current_nfa

    def thompson(self) -> NFA[int]:

        max_q = max(self.current_nfa.K)
        q0_nfa = max_q + 1
        f_nfa = set()
        f_nfa.add(q0_nfa + 1)
        f_aux = f_nfa.copy().pop()

        k_nfa = self.current_nfa.K
        k_nfa = k_nfa.union({q0_nfa})
        k_nfa = k_nfa.union(f_nfa)

        transitions_nfa = self.current_nfa.d
        transitions_nfa[(q0_nfa, EPSILON)] = {self.current_nfa.q0, f_aux}
        k_nfa = k_nfa.union({self.current_nfa.q0, f_aux})
        f = self.current_nfa.F.copy()
        transitions_nfa[(f.pop(), EPSILON)] = {self.current_nfa.q0, f_aux}
        k_nfa = k_nfa.union({self.current_nfa.q0, f_aux})

        return NFA(self.current_nfa.S, k_nfa, q0_nfa, transitions_nfa, f_nfa)


class PlusMark(Regex):
    def __init__(self, current_nfa: NFA):
        self.current_nfa = current_nfa

    def thompson(self) -> NFA[int]:

        max_q = max(self.current_nfa.K)
        q0_nfa = max_q + 1
        f_nfa = set()
        f_nfa.add(q0_nfa + 1)
        f_aux = f_nfa.copy().pop()

        k_nfa = self.current_nfa.K
        k_nfa = k_nfa.union({q0_nfa})
        k_nfa = k_nfa.union(f_nfa)

        transitions_nfa = self.current_nfa.d
        transitions_nfa[(q0_nfa, EPSILON)] = {self.current_nfa.q0}
        k_nfa = k_nfa.union({self.current_nfa.q0, f_aux})
        f = self.current_nfa.F.copy()
        transitions_nfa[(f.pop(), EPSILON)] = {self.current_nfa.q0, f_aux}
        k_nfa = k_nfa.union({self.current_nfa.q0, f_aux})



        return NFA(self.current_nfa.S, k_nfa, q0_nfa, transitions_nfa, f_nfa)


class QuestionMark(Regex):
    def __init__(self, current_nfa: NFA):
        self.current_nfa = current_nfa

    def thompson(self) -> NFA[int]:

        max_q = max(self.current_nfa.K)

        q0_nfa = max_q + 1
        f_nfa = set()
        f_nfa.add(max_q+ 2)
        f_aux = f_nfa.copy().pop()

        k_nfa = self.current_nfa.K
        k_nfa = k_nfa.union({q0_nfa})
        k_nfa = k_nfa.union(f_nfa)

        transitions_nfa = self.current_nfa.d
        transitions_nfa[(q0_nfa, EPSILON)] = {self.current_nfa.q0, f_aux}
        k_nfa = k_nfa.union({self.current_nfa.q0, f_aux})
        f = self.current_nfa.F.copy()
        transitions_nfa[(f.pop(), EPSILON)] = f_nfa

        return NFA(self.current_nfa.S, k_nfa, q0_nfa, transitions_nfa, f_nfa)












