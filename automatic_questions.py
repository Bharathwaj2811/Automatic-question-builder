import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import string

# Download NLTK data (if necessary)
nltk.download('punkt')

# Function to generate MCQs from a given paragraph
def generate_mcq(paragraph, num_questions=1):
    # Step 1: Split the paragraph into sentences
    sentences = sent_tokenize(paragraph)

    # Step 2: Select a sentence to form a question from (could be random or based on key info)
    selected_sentences = random.sample(sentences, num_questions)

    mcqs = []

    for sentence in selected_sentences:
        # Step 3: Pick a word or phrase from the sentence to generate a question
        words = word_tokenize(sentence)
        
        # Remove punctuation and stopwords
        words = [word for word in words if word.isalnum()]

        # Ensure there's enough meaningful content to ask about
        if len(words) > 3:
            key_word = random.choice(words)  # Randomly choose a word to be the correct answer

            # Generate a question by replacing the chosen word with a blank
            question = sentence.replace(key_word, "_")

            # Step 4: Generate wrong choices (simple logic, can be enhanced)
            distractors = [random.choice(words) for _ in range(3)]  # Simple word-based distractors
            distractors.append(key_word)  # Correct answer
            random.shuffle(distractors)  # Shuffle the answer choices

            # Store the question and its answer choices
            mcqs.append({
                'question': question,
                'choices': distractors,
                'correct_answer': key_word
            })

    return mcqs

# Main Program to Accept User Input
if __name__ == "__main__":  # Fixed the condition here
    # Input: User provides a paragraph
    paragraph = input("Enter a paragraph: ")

    # Set the number of questions you want to generate
    num_questions = int(input("Enter the number of questions to generate: "))

    # Generate MCQs
    mcqs = generate_mcq(paragraph, num_questions)

    # Output: Display the generated MCQs
    for i, mcq in enumerate(mcqs):
        print(f"\nQ{i+1}: {mcq['question']}")
        for idx, choice in enumerate(mcq['choices'], 1):
            print(f"   {idx}. {choice}")
        print(f"Correct Answer: {mcq['correct_answer']}\n")
