import re

UNITS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]

TENS = [
    "ten",
    "twenty",
    "thirty",
    "fourty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]

GROUPS = [
    "",
    "thousand",
    "million",
    "billion",
    "trillion",
]

def number_as_string_grouped(number):
    stack = []
    if number % 100 >= 20:
        stack.insert(0, TENS[((number % 100) // 10)-1] + " " + number_as_string_grouped(number%10))
    else:
        stack.insert(0, UNITS[number%100-1])        
    if number >= 100:
        stack.insert(0, number_as_string_grouped(number//100) + " hundred")
    return (" ".join(stack))

def number_as_string(number):
    if type(number) == str:
        number = int(number)
    stack = []
    group = 0
    if number == 0:
        return "zero"
    while number > 0:
        appendix = GROUPS[group]
        group += 1
        lit = number_as_string_grouped(number % (10**(3*group)))
        stack.insert(0,lit + " " + appendix)
        number = number // 10**(3*group)
    return (" ".join(stack)).strip()


def numbers(source_text):
    text = source_text
    for m in re.finditer(r"[0-9]+", source_text):
        text = text.replace(m.group(), number_as_string(m.group()))
    return text
