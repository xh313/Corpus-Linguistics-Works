def lemmatize(string):
    """
    Takes a Finnish string and lemmatize it.
    :param string: the string to be lemmatized
    :return: a list of lemmas
    """
    import libvoikko
    import re

    v = libvoikko.Voikko(u"fi")  # Define a Voikko class for Finnish

    txt = string

    # Pre-process the text
    txt = txt.lower()
    txt = txt.replace('\n', ' ')
    txt = txt.strip()
    txt = re.sub(r'[^\w]', ' ', txt)  # Remove punctuations
    txt = re.sub(r'[0-9]+', '', txt)
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