import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Download the necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')

# Example usage
sentence = "This is a simple sentence."
tokens = word_tokenize(sentence)
tags = pos_tag(tokens)
print(tags)
