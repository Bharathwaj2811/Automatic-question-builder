import requests
import random
import re
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, RegexpParser
from nltk.corpus import wordnet as wn
from db import create_connection, close_connection  # Import functions from db.py

class ObjectiveTest:

    def __init__(self, data, noOfQues):
        self.summary = data
        self.noOfQues = noOfQues

    def get_trivial_sentences(self):
        sentences = sent_tokenize(self.summary)
        trivial_sentences = []
        for sent in sentences:
            trivial = self.identify_trivial_sentences(sent)
            if trivial:
                trivial_sentences.append(trivial)
        return trivial_sentences

    def identify_trivial_sentences(self, sentence):
        tokens = word_tokenize(sentence)
        tags = pos_tag(tokens)
        if tags[0][1] == "RB" or len(tokens) < 4:
            return None
        
        noun_phrases = []
        grammar = r"""
            CHUNK: {<NN>+<IN|DT>*<NN>+}
                {<NN>+<IN|DT>*<NNP>+}
                {<NNP>+<NNS>*}
            """
        chunker = RegexpParser(grammar)
        pos_tokens = pos_tag(tokens)
        tree = chunker.parse(pos_tokens)

        for subtree in tree.subtrees():
            if subtree.label() == "CHUNK":
                temp = " ".join([sub[0] for sub in subtree])
                noun_phrases.append(temp.strip())
        
        replace_nouns = []
        for word, _ in tags:
            for phrase in noun_phrases:
                if phrase[0] == '\'':
                    break
                if word in phrase:
                    replace_nouns.extend(phrase.split()[-2:])
                    break
            if not replace_nouns:
                replace_nouns.append(word)
            break
        
        if not replace_nouns:
            return None
        
        val = min(len(i) for i in replace_nouns)
        
        trivial = {
            "Answer": " ".join(replace_nouns),
            "Key": val
        }

        if len(replace_nouns) == 1:
            trivial["Similar"] = self.answer_options(replace_nouns[0])
        else:
            trivial["Similar"] = []
        
        replace_phrase = " ".join(replace_nouns)
        blanks_phrase = "__________ " * len(replace_nouns)
        expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
        question_sentence = expression.sub(blanks_phrase.strip(), sentence)
        trivial["Question"] = question_sentence
        return trivial

    @staticmethod
    def answer_options(word):
        synsets = wn.synsets(word, pos="n")
        if not synsets:
            return []
        
        synset = synsets[0]
        hypernym = synset.hypernyms()
        if not hypernym:
            return []
        
        hypernym = hypernym[0]
        hyponyms = hypernym.hyponyms()
        similar_words = []
        for hyponym in hyponyms:
            similar_word = hyponym.lemmas()[0].name().replace("_", " ")
            if similar_word != word:
                similar_words.append(similar_word)
            if len(similar_words) == 8:
                break
        return similar_words

    def generate_test(self):
        trivial_pair = self.get_trivial_sentences()
        question_answer = [item for item in trivial_pair if item["Key"] > int(self.noOfQues)]
        
        questions = []
        answers = []
        options_list = []
        
        while len(questions) < int(self.noOfQues):
            if not question_answer:
                break
            
            rand_num = np.random.randint(0, len(question_answer))
            selected_item = question_answer[rand_num]

            if selected_item["Question"] not in questions:
                questions.append(selected_item["Question"])
                answers.append(selected_item["Answer"])
                # Generate options including the correct answer
                correct_answer = selected_item["Answer"]
                options = self.generate_options(correct_answer, selected_item["Similar"])
                options_list.append(options)
        
        return questions, answers, options_list

    @staticmethod
    def generate_options(correct_answer, similar_words):
        # Shuffle the options and include the correct answer
        options = list(set(similar_words))  # Remove duplicates
        options.append(correct_answer)  # Add correct answer
        np.random.shuffle(options)  # Shuffle options
        return options[:4]  # Return only 4 options

def fetch_related_terms(keyword):
    # Replace this URL with your actual API endpoint
    url = f"http://your-api-endpoint.com/get_related_terms?keyword={keyword}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Assume API returns a list of terms
    return []

def generate_incorrect_options(keyword):
    """
    Generate a list of incorrect options based on the keyword.
    """
    terms = fetch_related_terms(keyword)
    return random.sample(terms, 3) if len(terms) >= 3 else ["Option 1", "Option 2", "Option 3"]

def insert_incorrect_options(question_id, incorrect_options):
    """
    Insert generated incorrect options into the incorrect_options table.
    """
    connection = create_connection()  # Use the db connection from db.py
    try:
        cursor = connection.cursor()

        for option in incorrect_options:
            cursor.execute(
                "INSERT INTO incorrect_options (question_id, incorrect_option) VALUES (%s, %s)",
                (question_id, option)
            )
        connection.commit()

    except Exception as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        close_connection(connection)  # Close the connection

def add_question_with_answer(question_text, answer_text):
    """
    Add a new question and answer to the question_bank and generate incorrect options.
    """
    connection = create_connection()  # Use the db connection from db.py
    try:
        cursor = connection.cursor()

        # Insert the new question and answer
        cursor.execute(
            "INSERT INTO question_bank (question, answer) VALUES (%s, %s)",
            (question_text, answer_text)
        )
        question_id = cursor.lastrowid  # Get the ID of the newly inserted question
        connection.commit()

        # Generate incorrect options based on the answer
        incorrect_options = generate_incorrect_options(answer_text)
        # Store the generated options in the incorrect_options table
        insert_incorrect_options(question_id, incorrect_options)

        print(f"Question added with ID: {question_id} and incorrect options generated.")

    except Exception as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        close_connection(connection)  # Close the connection

# Example usage
if __name__ == "__main__":
    summary = "Paris is the capital of France. It is known for its art, fashion, and culture."
    no_of_questions = 5

    # Create an instance of ObjectiveTest
    objective_test = ObjectiveTest(summary, no_of_questions)

    # Generate questions, answers, and options
    questions, answers, options_list = objective_test.generate_test()

    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        options = options_list[i]
        
        # Add each question and its answer to the database
        add_question_with_answer(question, answer)

        # Assuming options_list[i] contains both the correct answer and incorrect options
        incorrect_options = [opt for opt in options if opt != answer]
        
        # Retrieve the last question_id inserted and store incorrect options in the database
        question_id = i + 1  # Example ID, adjust based on your logic
        insert_incorrect_options(question_id, incorrect_options)
