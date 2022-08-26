from django.test import TestCase
from django.contrib.auth.models import User
import json

test_user = {"username": "testuser", "password": "testpassword"}
second_user = {"username": "seconduser", "password": "secondpassword"}

class QuestionsTest(TestCase):
    def setUp(self):
        new_user = User.objects.create(username=test_user["username"])
        new_user.set_password(test_user["password"])
        new_user.save()
        new_second_user = User.objects.create(username=second_user["username"])
        new_second_user.set_password(second_user["password"])
        new_second_user.save()

    def get_token(self):
        res = self.client.post('/api/token/',
           data=json.dumps({
               'username': test_user["username"],
               'password': test_user["password"],
           }),
           content_type='application/json',
        )
        result = json.loads(res.content)
        self.assertTrue("access" in result)
        return result["access"]

    def get_second_token(self):
        res = self.client.post('/api/token/',
           data=json.dumps({
               'username': second_user["username"],
               'password': second_user["password"],
           }),
           content_type='application/json',
        )
        result = json.loads(res.content)
        self.assertTrue("access" in result)
        return result["access"]

    def test_post_question(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [])
        self.assertTrue(len(result["alphanumeric_code"]) == 6)
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.post('/api/quizes/{}/questions/'.format(result["id"]),
                               data=json.dumps({'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        question = json.loads(res.content)["data"]
        self.assertEquals(question, {'id': 1, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 1}]})
        
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [question])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.post('/api/quizes/{}/questions/'.format(result["id"]),
                               data=json.dumps({'question': 'Question test 2', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        question2 = json.loads(res.content)["data"]
        self.assertEquals(question2, {'id': 2, 'question': 'Question test 2', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 2}]})
        
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [question, question2])
        self.assertEquals(result["is_published"], False)

    def test_put_and_get_question(self):
        token = self.get_token()
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        result = json.loads(res.content)["data"]
        quiz_id = result["id"]
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["questions"], [{'id': 1, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 1}]}])
        
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        question["id"] = 1
        question["answers"][0]["id"] = 1
        self.assertEquals(result["questions"], [question])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.post('/api/quizes/{}/questions/'.format(result["id"]),
                               data=json.dumps({'question': 'Question test 2', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        question2 = json.loads(res.content)["data"]
        self.assertEquals(question2, {'id': 2, 'question': 'Question test 2', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 2}]})
        res = self.client.get('/api/quizes/{}/questions/{}/'.format(result["id"], question2["id"]),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(question2, json.loads(res.content)["data"])
        
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [question, question2])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(result["id"], question2['id']),
                               data=json.dumps({'question': 'Question test 2 changed'}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        question2 = json.loads(res.content)["data"]
        self.assertEquals(question2, {'id': 2, 'question': 'Question test 2 changed', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'id': 2, 'is_correct': True}]})
        
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [question, question2])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(result["id"], question2['id']),
                               data=json.dumps({'question': 'Question test 2 changed again', 'answers': []}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        question2 = json.loads(res.content)["data"]
        
        res = self.client.get('/api/quizes/' + str(result["id"]) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["title"], 'Test quiz')
        self.assertEquals(result["questions"], [question, question2])
        self.assertEquals(result["is_published"], False)
        
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(result["id"], question2['id']),
                               data=json.dumps({'answers': [{'answer': 'ans 1', 'is_correct': False}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        question2 = json.loads(res.content)["data"]
        self.assertEquals(question2, {'question': 'Question test 2 changed again',
                                      'id': 2, 'is_multiple_answers': True,
                                      'answers': [{'answer': 'ans 1', 'is_correct': False, 'id': 3}]})
        res = self.client.get('/api/quizes/{}/questions/{}/'.format(result["id"], question2['id']),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        question2_get = json.loads(res.content)["data"]
        self.assertEquals(question2, question2_get)

    def test_delete_question(self):
        token = self.get_token()
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        result = json.loads(res.content)["data"]
        quiz_id = result["id"]
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["questions"], [{'id': 1, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 1}]},
                                              {'id': 2, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 2}]},
                                              {'id': 3, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 3}]}])

        res = self.client.get('/api/quizes/' + str(quiz_id) + "/questions/1/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        question1 = question
        question1["id"] = 1
        question1["answers"][0]["id"] = 1
        self.assertEquals(question1, data)
        res = self.client.delete('/api/quizes/' + str(quiz_id) + "/questions/1/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 410)
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/questions/1/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)
        
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["questions"], [{'id': 2, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 2}]},
                                              {'id': 3, 'question': 'Question test', 'is_multiple_answers': True,
                                                'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 3}]}])
        
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/questions/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data, [{'id': 2, 'question': 'Question test', 'is_multiple_answers': True,
                                  'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 2}]},
                                 {'id': 3, 'question': 'Question test', 'is_multiple_answers': True,
                                  'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 3}]}])
    
    def test_wrong_gets(self):
        token = self.get_token()
        second_token = self.get_second_token()
        res = self.client.get('/api/quizes/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        self.assertEquals(json.loads(res.content), {"data": [], "count" :0})
        res = self.client.get('/api/quizes/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)
        self.assertEquals(json.loads(res.content), {"detail": "Not found"})
        res = self.client.get('/api/quizes/1/questions/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)
        self.assertEquals(json.loads(res.content), {"detail": "Not found"})
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        
        res = self.client.get('/api/quizes/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {second_token}'
                               )
        self.assertEquals(res.status_code, 200)
        self.assertEquals(json.loads(res.content), {"data": [], "count" :0})
        res = self.client.get('/api/quizes/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {second_token}'
                               )
        self.assertEquals(res.status_code, 401)
        self.assertEquals(json.loads(res.content), {"detail": "Not authorized"})
        res = self.client.get('/api/quizes/1/questions/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {second_token}'
                               )
        self.assertEquals(res.status_code, 401)
        self.assertEquals(json.loads(res.content), {"detail": "Not authorized"})
        res = self.client.get('/api/quizes/1/questions/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        res = self.client.get('/api/quizes/1/questions/4/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)
        res = self.client.delete('/api/quizes/1/questions/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 410)
        res = self.client.get('/api/quizes/1/questions/1/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)
        
        res = self.client.post('/api/quizes/1/questions/',
                               data=json.dumps(question),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        res = self.client.post('/api/quizes/5/questions/',
                               data=json.dumps(question),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 404)

    def test_editing_some_answers_in_question(self):
        token = self.get_token()
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        result = json.loads(res.content)["data"]
        quiz_id = result["id"]
        res = self.client.get('/api/quizes/' + str(quiz_id) + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        data = json.loads(res.content)["data"]
        question1 = {'id': 1, 'question': 'Question test', 'is_multiple_answers': True,
                     'answers': [{'answer': 'Ans 1', 'is_correct': True, 'id': 1}]}
        self.assertEquals(data["questions"][0], question1)
        
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'title': "Test quiz"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'question': "New question??"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        question1["question"] = "New question??"
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'answers': [{"id": 1, "answer": "new answer text"}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        question1["answers"][0]["answer"] = "new answer text"
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'answers': [{"id": 2, "answer": "question does not exist"}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'answers': [{"answer": "new answer", "is_correct": False}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        question1["answers"].append({"answer": "new answer", "is_correct": False, "id": 4})
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
        res = self.client.put('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               data=json.dumps({'answers': []}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        res_get = self.client.get('/api/quizes/{}/questions/{}/'.format(quiz_id, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res_get.status_code, 200)
        self.assertEquals(res_get.content, res.content)
        question1["answers"] = []
        new_question = json.loads(res.content)["data"]
        self.assertEquals(question1, new_question)
    
    def test_wrong_types(self):
        token = self.get_token()
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': ["title", "bad"],
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"title": "This field must be string"}]})
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'questions': {"question": "only one, bad"}}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"title": "This field must be string"},
                                                               {"questions": "This field must be a list"},]})
        res = self.client.post('/api/quizes/1/questions/',
                               data=json.dumps({"question": 10}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"question": "This field must be string"}]})
        res = self.client.post('/api/quizes/1/questions/',
                               data=json.dumps({"answers": {"answer": "only one instead of list."}}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"answers": "This field must be a list"}]})
        res = self.client.post('/api/quizes/1/questions/',
                               data=json.dumps({"answers": [{"answer": 19}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"answer": "This field must be string"}]})
        res = self.client.post('/api/quizes/1/questions/',
                               data=json.dumps({"answers": [{"is_correct": "yes"}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content), {"errors": [{"is_correct": "This field must be boolean"}]})
        
    def test_delete_answers(self):
        token = self.get_token()
        question = {'question': 'Question test', 'is_multiple_answers': True,'answers': [{'answer': 'Ans 1', 'is_correct': True},
                                                                                         {'answer': 'Ans 1', 'is_correct': True},
                                                                                         {'answer': 'Ans 1', 'is_correct': True}]}
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz",
                                                'questions': [question, question, question]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        res = self.client.get('/api/quizes/{}/questions/{}/'.format(1, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        question = json.loads(res.content)["data"]
        self.assertEquals(len(question["answers"]), 3)
        res = self.client.delete('/api/quizes/{}/questions/{}/answers/'.format(1, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 410)
        self.assertEquals(json.loads(res.content)["detail"], "deleted all answers")
        res = self.client.get('/api/quizes/{}/questions/{}/'.format(1, 1),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        question = json.loads(res.content)["data"]
        self.assertEquals(len(question["answers"]), 0)