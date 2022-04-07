import voikko_string_lemmatizer as fi_str
import voikko_file_lemmatizer as fi_file

pos_lemma = fi_file.lemmatize('pos_list.txt')
neg_lemma = fi_file.lemmatize('neg_list.txt')

def get_word_counts(word_list):
    """
    Takes as input a lemma list and returns a dictionary with the
    number of times each word occurred in that file.
    :param list: The file to be counted
    :return: A dictionary containing the number of occurrences for each word
    """

    dictionary = {}
    #word_list = []

    #for l in listname:
        #word_list += l.split()

    for word in word_list:
      word_stemmed = word  # No stemming
      #word_stemmed = fistemmer.stem(word)  # stemming
      if word_stemmed not in dictionary:
          dictionary[word_stemmed] = 1
      else:
          dictionary[word_stemmed] += 1

    return dictionary


def counts_to_probs(dictionary, num):
    """
    Takes a dictionary and a number and generates a new dictionary with
    the same keys where each value has been divided by the input number.
    :param dictionary: The dictionary to be operated on
    :param num: The number to be divided
    :return: A dictionary in which all values for each key have been divided by num
    """
    for word in dictionary:
        dictionary[word] /= num

    return dictionary


def train_model(listname, word_list):
    """
    Takes as input a listname containing examples and returns a dictionary with the word probabilities.
    :param listname: The name of the list to be counted and calculated
    :return: A dictionary containing the probability of the occurrences of each word type
    """
    lines = len(listname)
    counts = get_word_counts(word_list)
    probs = counts_to_probs(counts, lines)
    return probs


def get_probability(dictionary, string):  # This is why it's finnish specific!
    """
    Takes as input two parameters, a dictionary of word probabilities and a
    string (representing a review), and returns the probability of that review
    by multiplying the probabilities of each of the words in the review.
    :param dictionary: The dictionary containing the probability data
    :param string: The string to be evaluated on
    :return: The product of teh probability of each of the words in the string
    """
    string = string.lower()
    word_list = fi_str.lemmatize(string)  # Create a list of words from the input str
    probs = 1  # Initialise

    for word in word_list:
        if word in dictionary:
            probs *= dictionary[word]
        else:
            probs *= 1 / 11000

    return probs


def classify(string, pos_dict, neg_dict):
    """
    Takes a string (a review), a positive and a negative model. Returns “positive” or
    “negative” depending on which model has the highest probability for the review.
    Ties goes to positive.
    :param string: The review to be classified
    :param pos_dict: The positive model (dict)
    :param neg_dict: The negative model (dict)
    :return: “positive” or “negative” depending on which model has the highest probability for the review.
    """
    pos_probs = get_probability(pos_dict, string)
    neg_probs = get_probability(neg_dict, string)
    if (pos_probs - neg_probs) >= 0:
        return 'positive'
    else:
        return 'negative'


def sentiment_analyzer_interactive(pos_list, neg_list):
    """
    An interactive function that takes two files as input, a positive
    examples file and a negative examples file. It would train a positive
    and negative model using these files and then repeatedly ask the user
    to enter a sentence and then output the classification of that sentence
    (as positive or negative). A blank line/sentence should terminate the function.
    :param pos_file: File name of the positive training data
    :param neg_file: File name of the negative training data
    """
    pos_dict = train_model(pos_list, pos_lemma)
    neg_dict = train_model(neg_list, neg_lemma)  # Train the models

    print('Blank line terminates.')
    string = input('Enter a sentence: ')
    while string != '':
        print(classify(string, pos_dict, neg_dict))
        string = input('Enter a sentence: ')



def get_accuracy(pos_train, neg_train, pos_test, neg_test):
    """
    A function that would train the model (i.e., both positive and negative counts) and then classify
    all of the test examples (both positive and negative) and keep track of the accuracy of the
    model. It would print out three scores: the accuracy on the positive test examples,
    the accuracy on the negative test examples, and the accuracy on all of the test examples.
    :param pos_test_name: File name of the positive testing data
    :param neg_test_name: File name of the negative testing data
    :param pos_train: File name of the positive training data
    :param neg_train: File name of the negative training data
    """
    pos_dict = train_model(pos_train, pos_lemma)
    neg_dict = train_model(neg_train, neg_lemma)  # Train the models

    pos_total = len(pos_test)
    neg_total = len(neg_test)  # Total num of pos & neg reviews

    pos_actual = 0
    neg_actual = 0  # Initialise

    for l in pos_test:
        if classify(l, pos_dict, neg_dict) == 'positive':
            pos_actual += 1

    for l in neg_test:
        if classify(l, pos_dict, neg_dict) == 'negative':
            neg_actual += 1

    pos_accuracy = pos_actual / pos_total
    neg_accuracy = neg_actual / neg_total
    total_accuracy = (pos_actual + neg_actual) / (pos_total + neg_total)

    print('Positive accuracy: ', pos_accuracy)
    print('Negative accuracy: ', neg_accuracy)
    print('Total accuracy: ', total_accuracy)


def sentiment_analyzer_batch(filename, pos_list, neg_list):
    pos_dict = train_model(pos_list, pos_lemma)
    neg_dict = train_model(neg_list, neg_lemma)  # Train the models

    file = open(filename, 'r')
    pos_count = 0
    neg_count = 0
    pos_posts = []
    neg_posts = []
    for l in file:
        if classify(l, pos_dict, neg_dict) == 'positive':
            pos_posts.append(l)
            pos_count += 1
        elif classify(l, pos_dict, neg_dict) == 'negative':
            neg_posts.append(l)
            neg_count += 1
    file.close()

    print('Positives: ' + str(pos_count))
    print('Negatives: ' + str(neg_count))
    print('Portion Positive: ' + str(pos_count / (pos_count + neg_count)))

    separated_posts = [pos_posts, neg_posts]

    return separated_posts



# Testing
pos_list = fi_file.to_list('pos_list.txt')
neg_list = fi_file.to_list('neg_list.txt')
"""
from korpi_processor import *
get_accuracy(pos_list, neg_list, pos_korpi, neg_korpi)
"""
sentiment_analyzer_batch('1_Suomi.txt', pos_list, neg_list)