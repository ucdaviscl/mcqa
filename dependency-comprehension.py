import sys, io, spacy, nltk, math
from spacy.tokens import Doc
from nltk.tokenize import word_tokenize

raw = io.open('%s' % sys.argv[1], mode='r', encoding='utf-8')
processed = io.open('%s.depanswers' % sys.argv[1], mode='w', encoding='utf-8')

nlp = spacy.load('en')

def copy_passage(raw, text):
    next = raw.read(1)

    #bypass id
    while next != '\t':
        next = raw.read(1)
        #check EOF
        if next == '':
            return 0

    #bypass metadata
    next = raw.read(1)
    while next != '\t':
        next = raw.read(1)

    #copy passage
    print('copying passage ...')
    next = raw.read(1)
    while next != '\t':
        #bypass "\newline\newline"
        if next == '\\':
            raw.read(15)
            #next = '\n'
            next = raw.read(1)
            continue

        text += next
        next = raw.read(1)
    text += next
    print('end - ' + next)

    #tokenize and parse
    doc = nlp(text)

    return doc


def copy_question(raw, text):
    next = raw.read(1)

    #bypass 'multiple' or 'one'
    if next == 'm':
        raw.read(9)
    elif next == 'o':
        raw.read(4)
    else:
        print('error')
        print(next)

    #copy question
    print('copying question ...')
    next = raw.read(1)
    while next != '\t':
        text += next
        next = raw.read(1)
    text+= next

    #tokenize and parse
    doc = nlp(text)

    return doc

def copy_answer(raw, text, num, ans):
    #copy answers
    if ans < 3:
        next = raw.read(1)
        print('copying answer ... ' + str(ans) + ' - ' + next)
        while next!= '\t':
            text += next
            next = raw.read(1)
        text += next
    else:
        if num < 3:
            next = raw.read(1)
            print('copying answer ... 3 - ' + next)
            while next!= '\t':
                text += next
                next = raw.read(1)
            text += next
        else:
            next = raw.read(1)
            print('copying answer ... 3 - ' + next)
            while next!= '\n':
                text += next
                next = raw.read(1)
            text += next
        print('end - ' + next)

        #end passage/question set
        if num < 3:
            text += '\n'

    #tokenize and parse
    doc = nlp(text)

    return doc

#initialize variables
output = ''
text = ''
parsed = ''
Z = [None] * 4
answer_score = [float(00)] * 4
q_words = ['who', 'what', 'when', 'where', 'why', 'how', 'Who', 'What', 'When', 'Where', 'Why', 'How']

#loop through passages
while True:
    X = copy_passage(raw, text)
    #break if EOF
    if X == 0:
        break

    #loop through first 3 questions
    for i in range(4):
        answer_score = [float(00)] * 4
        print(i)
        Y = copy_question(raw, text)

        #retrieve answers
        for j in range(4):
            Z[j] = copy_answer(raw, text, i, j)

        #loop through words in question and find a q-word
        for token in Y:
            if token.text in q_words:
                print('Q-Word: ' + token.text)
                key = token.dep
                head = token.head.text

                #loop through text to find a matching word for q-word
                for token in X:
                    if token.dep == key and token.head.text == head:
                        print('Token Match: ' + token.text)

                        #check similarity with answer choices
                        for j in range(4):
                            sim = float(token.similarity(Z[j]))
                            print (str(j) + ' - Similarity: ' + str(sim))

                            if answer_score[j] < sim:
                                answer_score[j] = sim

        for answer in answer_score:
            print(answer)

        #find best answer and output corresponding value
        BEST = max(answer_score)

        if BEST == 0:
            output += 'E'
            print('E')
        elif BEST == answer_score[0]:
            output += 'A'
            print('A')
        elif BEST == answer_score[1]:
            output += 'B'
            print('B')
        elif BEST == answer_score[2]:
            output += 'C'
            print('C')
        elif BEST == answer_score[3]:
            output += 'D'
            print('D')
        else:
            output += 'E'
            print('E')

        if i < 3:
            output += '\t'

    output += '\n'

processed.write(output)

raw.close()
processed.close()
