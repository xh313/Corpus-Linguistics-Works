# Import the Voikko library
import libvoikko
import re


def lemmatize(file):
    """
    Takes a file that has a string on each line and returns a lemma list.
    :param file: The file to be lemmatized
    :return: Lemma list
    """
    # Import the Voikko library
    import libvoikko
    import re

    # Define a Voikko class for Finnish
    v = libvoikko.Voikko(u"fi")

    # Some Finnish text
    infile = open(file, 'r')
    txt = infile.read()
    infile.close()

    # Pre-process the text
    txt = txt.lower().replace('\n', ' ')
    txt = txt.strip()
    txt = re.sub(r'[^\w]', ' ', txt)  # Remove punctuations
    txt = re.sub(r'\s{2,}', ' ', txt)  # Remove the multiple spaces

    # Split to list by space character
    word_list = txt.split(' ')

    # Initialize a list for base form words
    bf_list = []

    # Loop all words in the list
    for w in word_list:

        # Analyze the word with voikko
        voikko_dict = v.analyze(w)

        # Extract the base form, if the word is recognized
        if voikko_dict:
            bf_word = voikko_dict[0]['BASEFORM']
        # If word is not recognized, add the original word
        else:
            bf_word = w

        # Append to the list
        bf_list.append(bf_word)

    return bf_list


# Export results
def export(file, filename):
    outfile = open(filename + '.csv', 'w')
    outfile.write('lemma')

    for lemma in lemmatize(file):
        outfile.write('\n')
        outfile.write(lemma)

    outfile.close()


# File to list
def to_list(filename):
    file = open(filename, 'r')
    outlist = []
    
    for l in file:
        outlist.append(l)

    file.close()

    return outlist


# export('neg_list.txt','neg_lemma')
