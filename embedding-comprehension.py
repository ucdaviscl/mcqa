import sys, io

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

raw = io.open('%s' % sys.argv[1], mode='r', encoding='utf-8')
processed = io.open('%s.embedanswers' % sys.argv[1], mode='w', encoding='utf-8')

module_url = "https://tfhub.dev/google/universal-sentence-encoder/2"
print("Embedding module ...")
embed = hub.Module(module_url)

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

def run_and_find_similar(session_, input_tensor_, messages_, encoding_tensor):
  message_embeddings_ = session_.run(
      encoding_tensor, feed_dict={input_tensor_: messages_})
  corr = np.inner(message_embeddings_[:4], message_embeddings_[4])

  output = ''

  BEST = max(corr)

  if BEST == corr[0]:
      output = 'A'
      print('A')
  elif BEST == corr[1]:
      output = 'B'
      print('B')
  elif BEST == corr[2]:
      output = 'C'
      print('C')
  elif BEST == corr[3]:
      output = 'D'
      print('D')
  else:
      output = 'E'
      print('E')

  return output

#initialize variables
output = ''
text = ''
parsed = ''
passage_itr = 0

#loop through passages
while True:
    X = copy_passage(raw, text)
    print('Passage #' + str(passage_itr))

    #break if EOF
    if X == 0:
        break
    elif passage_itr >=1:
        break
    passage_itr += 1

    #loop through first 3 questions
    for i in range(4):
        print(i)
        Y = copy_question(raw, text)

        #initialize variables
        answer_choices = [None] * 4

        #loop through answer choices
        for j in range(4):
            Z = copy_answer(raw, text, i, j)
            answer_choices[j] = Y + Z

        answer_choices.append(X)

        similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
        similarity_message_encodings = embed(similarity_input_placeholder)
        with tf.Session() as session:
            session.run(tf.global_variables_initializer())
            session.run(tf.tables_initializer())
            ans = run_and_find_similar(session, similarity_input_placeholder, answer_choices, similarity_message_encodings)

        output += ans

        if i < 3:
            output += '\t'

    output += '\n'

processed.write(output)

raw.close()
processed.close()
