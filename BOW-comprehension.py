import sys, io, spacy, nltk, math
from spacy.tokens import Doc
from nltk.tokenize import word_tokenize

raw = io.open('%s' % sys.argv[1], mode='r', encoding='utf-8')
processed = io.open('%s.bowanswers' % sys.argv[1], mode='w', encoding='utf-8')

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

    return text


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

    return text

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

    return text

#initialize variables
output = ''
text = ''
parsed = ''

#loop through passages
while True:
    X = copy_passage(raw, text)
    #break if EOF
    if X == 0:
        break
    else:
        passage = word_tokenize(X)
        fd = nltk.FreqDist(passage)

    #loop through first 3 questions
    for i in range(4):
        print(i)
        Y = copy_question(raw, text)

        #initialize variables
        question = [None] * 4
        q_n = [None] * 4
        q_fd = [None] * 4
        P_A = [None] * 4
        P_A_PASSAGE = [None] * 4
        P_PASSAGE_A = [None] * 4
        P_A_w = [None] * 4

        for j in range(4):
            Z = copy_answer(raw, text, i, j)
            question[j] = nltk.word_tokenize(Y + Z)
            q_fd[j] = nltk.FreqDist(question[j])
            q_n[j] = q_fd[j].N()

        sum_n = q_n[0] + q_n[1] + q_n[2] + q_n[3]
        K = (q_fd[0] + q_fd[1] + q_fd[2] + q_fd[3]).B()

        for j in range(4):
            P_A[j] = q_n[j] / sum_n
            P_A_PASSAGE[j] = 1
            P_PASSAGE_A[j] = 0

        for w in passage:
            for j in range(4):
                P_A_w[j] = (q_fd[j][w] + 1) / (q_n[j] + K)
                P_PASSAGE_A[j] = P_A_PASSAGE[j] + math.log(P_A_w[j])

        for j in range(4):
            P_PASSAGE_A[j] = math.log(P_A[j]) + P_A_PASSAGE[j]

        BEST = max(P_PASSAGE_A)

        if BEST == P_PASSAGE_A[0]:
            output += 'A'
        elif BEST == P_PASSAGE_A[1]:
            output += 'B'
        elif BEST == P_PASSAGE_A[2]:
            output += 'C'
        elif BEST == P_PASSAGE_A[3]:
            output += 'D'
        else:
            output += 'E'

        if i < 3:
            output += '\t'

    output += '\n'

processed.write(output)

raw.close()
processed.close()
