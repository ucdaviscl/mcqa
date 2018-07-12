import sys, io, spacy
from spacy.tokens import Doc

raw = io.open('%s' % sys.argv[1], mode='r', encoding='utf-8')
processed = io.open('%s.prepped' % sys.argv[1], mode='w', encoding='utf-8')

nlp = spacy.load('en')

counter = 0

def copy_passage(raw, text):
    next = raw.read(1)

    #identify passage
    global counter
    if counter == 0:
        text += '\tPassage ' + str(counter) + '. '
    else:
        text += 'Passage ' + str(counter) + '. '
    counter += 1

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

    #tokenize and sentence parse
    output = ''
    doc = nlp(text)
    for sentence in doc.sents:
        ##for token in sentence:
        output += sentence.text ##+ ' '
        output += '\n'

    return output


def copy_question(raw, text, num):
    next = raw.read(1)

    #identify questions
    text += 'Question ' + str(num) + '.' + '\n'

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

    #copy answers
    for i in range(3):
        next = raw.read(1)
        print('copying answer ... ' + str(i) + ' - ' + next)
        while next!= '\t':
            text += next
            next = raw.read(1)
        text += next

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
        output += X
        output += '\t'

    #loop through first 3 questions
    for i in range(4):
        print(i)
        Y = copy_question(raw, text, i)
        output += Y
        output += '\t'



processed.write(output.rstrip())

raw.close()
processed.close()
