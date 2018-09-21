import sys, json, random
from rasa_nlu.model import Interpreter
from pprint import pprint


interpreter = Interpreter.load("models\\current\\nlu")

responses_file = sys.argv[1]
responses = json.load(open(responses_file))

while True:
    question = input("> ")
    response = interpreter.parse(question)
    #pprint(response)
    intent = response.get("intent").get("name")
    answers = responses.get(intent)
    answer = answers[random.randrange(len(answers))]
    print (answer)
