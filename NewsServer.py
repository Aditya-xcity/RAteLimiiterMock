from random import randint

news = {
    1: "canteen mein patties 5 rupaye mehngi ho gayi",
    2: "aaj lab cancel ho gayi",
    3: "kal practical hai, file complete kar lo",
    4: "Maggi 10 rupaye ki ho gayi",
    5: "aaj professor ne surprise test le liya",
    6: "college ki Wi-Fi phir se band ho gayi",
    7: "attendance portal down ho gaya",
    8: "aaj wali class online shift ho gayi",
    9: "canteen mein samose khatam ho gaye",
    10: "assignment submit karne ki deadline aaj hai"
}

def response():
    random_number = randint(1, len(news))
    return news[random_number]