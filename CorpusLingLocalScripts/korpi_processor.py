import re

pos_korpi = []
neg_korpi = []


infile = open('korp_all_sentences.txt', 'r')
all = infile.read()

infile.close()

cleaned = re.sub(r'\nb', r'\n', all)  # remove all the b leading each line
cleaned = re.sub('\n\'\:\)\'', '', cleaned)  # remove the lines with only :)
cleaned = re.sub('\n\'\:\(\'', '', cleaned)  # remove the lines with only :(
cleaned = re.sub('\'\n\'', '\n', cleaned)  # remove the quotation marks
cleaned = cleaned.replace('\\xc3\\xa4', 'ä')
cleaned = cleaned.replace('\\xc3\\xb6', 'ö')
splitted = cleaned.split('\n')

for line in splitted:
  if ':)' in line:
    pos_korpi.append(line[:-3])  # Exclude the :)
  else:
    neg_korpi.append(line[:-3])