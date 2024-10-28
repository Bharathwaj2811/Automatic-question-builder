import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import RegexpParser, pos_tag

class SubjectiveTest:

    def __init__(self, data, noOfQues):
        self.question_pattern = [
            "Explain in detail ",
            "Define ",
            "Write a short note on ",
            "What do you mean by "
        ]
        self.grammar = r"""
            CHUNK: {<NN>+<IN|DT>*<NN>+}
                   {<NN>+<IN|DT>*<NNP>+}
                   {<NNP>+<NNS>*}
        """
        self.summary = data
        self.noOfQues = noOfQues
    
    @staticmethod
    def word_tokenizer(sequence):
        return [word for sent in sent_tokenize(sequence) for word in word_tokenize(sent)]
    
    @staticmethod
    def create_vector(answer_tokens, tokens):
        return np.array([1 if tok in answer_tokens else 0 for tok in tokens])
    
    @staticmethod
    def cosine_similarity_score(vector1, vector2):
        def vector_value(vector):
            return np.sqrt(np.sum(np.square(vector)))
        v1 = vector_value(vector1)
        v2 = vector_value(vector2)
        v1_v2 = np.dot(vector1, vector2)
        return (v1_v2 / (v1 * v2)) * 100 if v1 and v2 else 0
    
    def generate_test(self):
        sentences = sent_tokenize(self.summary)
        cp = RegexpParser(self.grammar)
        question_answer_dict = {}

        for sentence in sentences:
            tagged_words = pos_tag(word_tokenize(sentence))
            tree = cp.parse(tagged_words)

            for subtree in tree.subtrees():
                if subtree.label() == "CHUNK":
                    temp = " ".join(sub[0] for sub in subtree).strip().upper()
                    if temp not in question_answer_dict and len(word_tokenize(sentence)) > 20:
                        question_answer_dict[temp] = sentence
                    elif temp in question_answer_dict:
                        question_answer_dict[temp] += " " + sentence

        keyword_list = list(question_answer_dict.keys())
        question_answer = []

        for _ in range(int(self.noOfQues)):
            if keyword_list:
                rand_num = np.random.randint(0, len(keyword_list))
                selected_key = keyword_list[rand_num]
                answer = question_answer_dict[selected_key]
                question = f"{self.question_pattern[rand_num % len(self.question_pattern)]}{selected_key}."
                question_answer.append({"Question": question, "Answer": answer})

        que, ans = [], []
        unique_questions = set()

        while len(que) < int(self.noOfQues) and question_answer:
            rand_num = np.random.randint(0, len(question_answer))
            question = question_answer[rand_num]["Question"]
            if question not in unique_questions:
                unique_questions.add(question)
                que.append(question)
                ans.append(question_answer[rand_num]["Answer"])

        return que, ans
