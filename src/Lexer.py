from src.DFA import DFA
from src.NFA import NFA
from .Regex import parse_regex


class Lexer:
    def __init__(self, spec):
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        # spec este o lista de forma (token, regex)
        self.spec = spec
        self.specList = []
        self.alphabets = set()

        for token, regex in spec:
            dfa = parse_regex(regex).thompson().subset_construction()
            self.alphabets.update(dfa.S)
            self.specList.append((token, dfa))

    def lex(self, word: str) -> list[tuple[str, str]] | None:

        # 1) lexeme:
        copy_word = word
        output_list = []
        nr_line = 0
        cut = 0
        start_index = 0
        end_index = len(word)


        accepted = False
        while True:
            end_index = len(word) - cut
            current_word = word[start_index:end_index]

            # oprire
            if cut >= len(word):
                break

            # pt fiecare cuvant vf daca am un DFA sa il accepte
            for token, dfa in self.specList:
                if dfa.accept(current_word):
                    output_list.append((token, current_word))
                    accepted = True
                    if current_word == "\n":
                        nr_line += 1
                    break
            # daca am acceptat nu mai tai din cuvant si il resetez
            # caut in cuvantul de la vechiul cut si dupa
            if accepted == True:
                start_index = start_index + len(current_word)
                cut = 0
                end_index = len(word)
                word = word[start_index:end_index]
                accepted = False
                start_index = 0
            # altfel tot tai din cuvant spre stanga pana gasesc
            else:
                cut += 1

        # 2) erori:
        output_list = self.check_error(output_list, copy_word)

        return output_list

    # eroarea apare daca lexemele concatenate nu fac cuvantul =>
    # nu s-a mai gasit longest match - in diferenta de cuv ramas e o eroare
    def check_error(self, outputList, word):

        checked_list = []
        error = str()
        lexem_concat = str()

        nr_char = 0
        len_line = 0
        nr_line = 0
        for token, lexem in outputList:
            lexem_concat += lexem

        # aflare char si nr linie:
        for i in range(len(lexem_concat)):
            if lexem_concat[i] == "\n":
                nr_line += 1
                len_line = 0
            else:
                len_line += 1

        # nr ch = numar caract de pe acea linie
        nr_char = len_line - 1
        index_next_ch = len(lexem_concat)

        # 1) EROARE:
        if lexem_concat != word:
            # 1) caract de la care difera este cel la len(lenxemTotal) din word
            # 1) no alternative: ...CH - ch nu e din niciun alfabet, daca e:
            #                   ...CH x => x != EOF
            # 2) EOF:            ...CH x => x = EOF
            symbol = word[index_next_ch]
            nr_char += 1

            if self.unknown_ch(symbol) == True:
                error = "No viable alternative at character " + str(nr_char) + ", line " + str(nr_line)
            else:
                index_next_ch += 1
                if index_next_ch >= len(word):
                    error = "No viable alternative at character EOF, line " + str(nr_line)
                else:
                    nr_char, nr_line = self.find_char(word, nr_char, nr_line, index_next_ch - 1)
                    error = "No viable alternative at character " + str(nr_char) + ", line " + str(nr_line)

            no_token = ""
            checked_list.append((no_token, error))
        # 2) FARA EROARE:
        else:
            checked_list = outputList

        return checked_list

    def unknown_ch(self, symbol):

        if symbol in self.alphabets:
            return False
        else:
            return True

    # ex: tokenul bun ar fi fost: ACG(A|C|T)*CT
    # cuvant ramas: ACGAAGCTCT =>eroarea apare la G
    # V.ERROR: starea finala = sink -> fst char care intra in sink da eroarea
    def find_char(self, word, nrChar, nrLine, indexNextCh):

        for _, dfa in self.specList:
            if dfa.accept(word[indexNextCh: len(word)]) == False:
                if dfa.currentState == frozenset():
                    return dfa.nrChar + nrChar, nrLine + dfa.nrLine