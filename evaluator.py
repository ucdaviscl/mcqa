import sys, io

test = io.open('%s' % sys.argv[1], mode='r', encoding='utf-8')
standard = io.open('%s' % sys.argv[2], mode='r', encoding='utf-8')
evalu = io.open('%s.evaluation' % sys.argv[1], mode='w', encoding='utf-8')

correct = 0
total = 0

output = ''
S = ' '
T = ' '

while S and T:
    #loop through questions in a passage
    for i in range(4):
        #get answer values
        T = test.read(1)
        S = standard.read(1)

        if not S and not T:
            break
        elif not S:
            output += '\nTest Incomplete\n'
            break
        elif not T:
            output += '\nTest Longer than Standard\n'
            break

        #cross-check
        if T == S:
            output += 'C'
            correct += 1
            #print(S + ' - ' + T + ' : Correct')
        else:
            output += 'I'
            #print(S + ' - ' + T + ' : Incorrect')
        total += 1

        if i < 3:
            output += '\t'

        test.read(1)
        standard.read(1)

    output += '\n'

output += '\n# Correct - ' + str(correct) + '\n'
output += 'Total # - ' + str(total) + '\n'
output += 'Percent Correct - ' + str(correct / total) + '\n'

evalu.write(output)

test.close()
standard.close()
evalu.close
