from django.test import TestCase
from django.contrib.auth.models import User
import json

test_user = {"username": "testuser", "password": "testpassword"}
second_user = {"username": "seconduser", "password": "secondpassword"}

class QuizesTest(TestCase):
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

    def test_add_quiz_forbidden(self):
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz"}),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 401)
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                               )
        self.assertEquals(res.status_code, 401)

    def test_add_quiz_ok(self):
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

    def test_add_quiz_wrong_data(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "questions": "question"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{"questions": "Questions must be a list"}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "questions": [{"bad": ""}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{"questions": "The following keys should not be given: ['bad']"}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "questions": [{"question": "question", "is_multiple_answers": 19}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': "Field 'is_multiple_answers' should be boolean"}])

    def test_check_before_publishing_quiz(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{"length": "Quiz must have up at least one question to be published"}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': {'0': [{'question': 'Question is required'},
                                                        {'answers': 'At least one answer is required'}]}}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": []}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': {'0': [{'answers': 'At least one answer is required'}]}}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes"}]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': {'0': [{'answers': 'At least one answer must be correct'}]}}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': {'0': [{'answers': 'If question is one-answer only, just one answer should be correct'}]}}])
        
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]},
                                                              {"question": "Is this a second question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{'questions': {'0': [{'answers': 'If question is one-answer only, just one answer should be correct'}],
                                                  '1': [{'answers': 'If question is one-answer only, just one answer should be correct'}]}}])

    def test_publishing_quiz(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]

    def test_editing_quiz(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": False,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]
        quiz_id = str(data["id"])
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': "New name"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["title"], "New name")
        quiz_info_response = self.client.get('/api/quizes/' + quiz_id + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(quiz_info_response.status_code, 200)
        data = json.loads(quiz_info_response.content)["data"]
        self.assertEquals(data["title"], "New name")
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': "New name 2", 'questions': []}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["title"], "New name 2")
        self.assertEquals(data["questions"], [])
        quiz_info_response = self.client.get('/api/quizes/' + quiz_id + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(quiz_info_response.status_code, 200)
        data = json.loads(quiz_info_response.content)["data"]
        self.assertEquals(data["title"], "New name 2")
        self.assertEquals(data["questions"], [])
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': "New name 2", 'questions': []}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["title"], "New name 2")
        self.assertEquals(data["questions"], [])
        quiz_info_response = self.client.get('/api/quizes/' + quiz_id + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(quiz_info_response.status_code, 200)
        data = json.loads(quiz_info_response.content)["data"]
        self.assertEquals(data["title"], "New name 2")
        self.assertEquals(data["questions"], [])
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'is_published': True}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors = json.loads(res.content)["errors"]
        self.assertEquals(errors, [{"length": "Quiz must have up at least one question to be published"}])
    
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'is_published': True, 'questions': [{'question': 'Q1',
                                                                                     'answers': [{'correct': True, 'answer': 'Answer 1'}]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["is_published"], True)
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': 'New title for published quiz'}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400)
        errors= json.loads(res.content)["errors"]
        self.assertEquals(errors, [{"published_quiz": "First unpublish the quiz and then you will be able to edit it"}])

    def test_edit_other_user_quiz(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": False,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]
        quiz_id = str(data["id"])
        
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': "New name"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEquals(data["title"], "New name")
        quiz_info_response = self.client.get('/api/quizes/' + quiz_id + "/",
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(quiz_info_response.status_code, 200)
        data = json.loads(quiz_info_response.content)["data"]
        self.assertEquals(data["title"], "New name")
        
        second_token = self.get_second_token()
        res = self.client.put('/api/quizes/' + quiz_id + "/",
                               data=json.dumps({'title': "New name"}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {second_token}'
                               )
        self.assertEquals(res.status_code, 401)
        data = json.loads(res.content)
        self.assertEquals(data, {"detail": "Not authorized"})

    def test_avoiding_access_without_token(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]
        
        quiz_info = self.client.get('/api/quizes/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(quiz_info.status_code, 200)
        data = json.loads(quiz_info.content)["data"]
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["title"], "Test quiz")
        
        quiz_info = self.client.get('/api/quizes/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer NOT{token}'
                               )
        self.assertEquals(quiz_info.status_code, 401)
        detail = json.loads(quiz_info.content)["detail"]
        self.assertEquals(detail, "Given token not valid for any token type")
    
    def test_publishing_quiz_and_getting_questions_to_play_without_token(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "is_multiple_answers": True,
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]
        
        quiz_info = self.client.get('/api/play/{}/'.format(data["alphanumeric_code"]),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 200)
        data = json.loads(quiz_info.content)["data"]
        self.assertEquals(data["title"], "Test quiz")
        self.assertEquals(data["is_published"], True)
        self.assertEquals(data["questions"], [{"question": "Is this a question?", "answers": [{"answer": "Yes"}, {"answer": "No"}]},
                                              {"question": "Is this a second question?", "answers": [{"answer": "Yes"}, {"answer": "No"}], "is_multiple_answers": True}])
    
    def test_asking_for_unpublished_quiz(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": False,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "is_multiple_answers": True,
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        data = json.loads(res.content)["data"]
        
        quiz_info = self.client.get('/api/play/{}/'.format(data["alphanumeric_code"]),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 404)
        detail = json.loads(quiz_info.content)["detail"]
        self.assertEquals(detail, "Not found")

    def test_submit_answers(self):
        token = self.get_token()
        res = self.client.post('/api/quizes/',
                               data=json.dumps({'title': "Test quiz", "is_published": True,
                                                "questions": [{"question": "Is this a question?",
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": False},]},
                                                              {"question": "Is this a second question?",
                                                               "is_multiple_answers": True,
                                                               "answers": [{"answer": "Yes", "correct": True},
                                                                           {"answer": "No", "correct": True},]}]}),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        quiz_data = json.loads(res.content)["data"]
        alphanumeric_code = quiz_data["alphanumeric_code"]
        
        quiz_info = self.client.post('/api/play/{}/'.format(alphanumeric_code),
                                     data=json.dumps({"answers": [[0], [0, 1]]}),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 200)
        data = json.loads(quiz_info.content)["data"]
        self.assertEquals(data, {"correct": 2})
        
        quiz_info = self.client.post('/api/play/{}/'.format(alphanumeric_code),
                                     data=json.dumps({"answers": [[0], [0, 1, 2]]}),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 200)
        data = json.loads(quiz_info.content)["data"]
        self.assertEquals(data, {"correct": 1})
        
        quiz_info = self.client.post('/api/play/{}/'.format(alphanumeric_code),
                                     data=json.dumps({"answers": [[], [1]]}),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 200)
        data = json.loads(quiz_info.content)["data"]
        self.assertEquals(data, {"correct": 0})
        
        quiz_info = self.client.post('/api/play/{}/'.format(alphanumeric_code),
                                     data=json.dumps({"answers": [[0, 1]]}),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 400)
        data = json.loads(quiz_info.content)["detail"]
        self.assertEquals(data, {"message": "You should send a list of answers, one per question"})
        
        quiz_info = self.client.post('/api/play/{}/'.format(alphanumeric_code),
                                     data=json.dumps({"answers": []}),
                               content_type='application/json',
                               )
        self.assertEquals(quiz_info.status_code, 400)
        data = json.loads(quiz_info.content)["detail"]
        self.assertEquals(data, {"message": "You should send a list of answers, one per question"})
