import requests
import json
import copy

LOCAL_URL = "http://127.0.0.1:8000"
TEST_USERS = [("testing1", "pass1"), ("testing2", "pass2")]
tokens = []
for username, password in TEST_USERS:
    requests.post(LOCAL_URL + "/api/register/", json={"username": username, "password": password})
    token = json.loads(requests.post(LOCAL_URL + "/api/token/",
                                     json={"username": username, "password": password}).content)["access"]
    tokens.append(token)
    print("Created user {}".format(username))

QUIZ = {"title": "Math small quiz", "questions": [{"question": "What is 1 + 1?", "is_multiple_answers": False,
                                                   "answers": [{"answer": "1", "correct": False},
                                                               {"answer": "2", "correct": True},
                                                               {"answer": "3", "correct": False},]},
                                                  {"question": "What is 1 + 2?", "is_multiple_answers": False,
                                                   "answers": [{"answer": "1", "correct": False},
                                                               {"answer": "2", "correct": False},
                                                               {"answer": "3", "correct": True},]},
                                                  {"question": "x^2 = 4, which values can x be?", "is_multiple_answers": True,
                                                   "answers": [{"answer": "1", "correct": False},
                                                               {"answer": "2", "correct": True},
                                                               {"answer": "-2", "correct": True},]},
                                                  {"question": "What is 1 + 1?", "is_multiple_answers": True,
                                                   "answers": [{"answer": "1", "correct": False},
                                                               {"answer": "2", "correct": True},
                                                               {"answer": "3", "correct": False},]}]}


for user_idx in [0, 1]:
    existing_quizes = json.loads(requests.get(LOCAL_URL + "/api/quizes/", headers={"Authorization": "Bearer {}".format(tokens[user_idx])}).content)["data"]
    if existing_quizes:
        print("Deleting {} quizes from {}".format(len(existing_quizes), TEST_USERS[user_idx][0]))
    for q in existing_quizes:
        requests.delete(LOCAL_URL + "/api/quizes/{}/".format(q["id"]), headers={"Authorization": "Bearer {}".format(tokens[0])})
    count_quizes = 33 if user_idx == 0 else 4
    print("Creating {} quizes for {}...".format(count_quizes, TEST_USERS[user_idx][0]))
    for i in range(count_quizes):
        q = copy.copy(QUIZ)
        q["title"] += " " + str(i + 1)
        if user_idx == 1:
            q["title"] = "Algebra small quiz " + str(i + 1)
        if i == count_quizes - 1:
            q['is_published'] = True
        requests.post(LOCAL_URL + "/api/quizes/", json=q,
                    headers={"Authorization": "Bearer {}".format(tokens[user_idx])})