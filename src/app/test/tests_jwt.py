from django.test import TestCase
from django.contrib.auth.models import User
import json

test_users = [
    {"username": "testuser1", "password": "testpassword1"},
    {"username": "testuser2", "password": "testpassword2"},
]

class LoginTest(TestCase):
    def setUp(self):
        for user in test_users:
            new_user = User.objects.create(username=user["username"])
            new_user.set_password(user["password"])
            new_user.save()

    def test_login(self):
        USER1 = test_users[0]
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'username': USER1["username"],
                                   'password': USER1["password"],
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)
        self.assertTrue("access" in result)
    
    def test_wrong_login(self):
        USER1 = test_users[0]
        USER2 = test_users[1]
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'username': USER1["username"],
                                   'password': USER2["password"],
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 401)
        result = json.loads(res.content)
        self.assertEquals(result, {'detail': 'No active account found with the given credentials'})

    def test_register(self):
        USER1 = test_users[0]
        res = self.client.post('/api/register/',
                               data=json.dumps({
                                   'username': USER1["username"],
                                   'password': USER1["password"],
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 403)
        result = json.loads(res.content)
        self.assertEquals(result, {'success': False, 'detail': 'User already exists'})
        
        res = self.client.post('/api/register/',
                               data=json.dumps({
                                   'username': "newuser",
                                   'password': "newpassword",
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)
        self.assertTrue(result['success'])
        self.assertTrue("access" in result)
        
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'username': "newuser",
                                   'password': "newpassword",
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)
        self.assertTrue("access" in result)

    def test_register_validation(self):
        res = self.client.post('/api/register/',
                               data=json.dumps({
                                   'username': "newuser",
                                   'password': "",
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 400)
        result = json.loads(res.content)
        self.assertEquals(result, {'success': False, 'detail': 'Username and password are required'})
        
        res = self.client.post('/api/register/',
                               data=json.dumps({
                                   'username': "newuser",
                                   'password': [1, 2],
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 400)
        result = json.loads(res.content)
        self.assertEquals(result, {'success': False, 'detail': 'Username and password must be strings'})
        
        res = self.client.post('/api/register/',
                               data=json.dumps({
                                   'username': "",
                                   'password': [1, 2],
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 400)
        result = json.loads(res.content)
        self.assertEquals(result, {'success': False, 'detail': 'Username and password are required'})