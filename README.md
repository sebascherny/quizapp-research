# API

## Installation and running
- If db.sqlite3 file exists, to start database from scratch, just remove it and run from src/:
```
python3 manage.py migrate
```

- Create a file .env in src/ containing the SECRET_KEY.

- To run the server locally:
```
python3 manage.py runserver
```

## Endpoints

### Users

- api/register/
    - POST: creates a user and refresh a new token. Example body:
    ```
    {
        "username": "MyName",
        "password": "MySecret.2"
    }
    ```
    Return example:
    ```
    {
        'success': True,
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYyMDI3OTQ1LCJpYXQiOjE2NjE0MjMxNDUsImp0aSI6IjJlYWY2MjMyY2ZmMzRkYmViYTM1ZDg3MzYzYzk0NWUwIiwidXNlcl9pZCI6MTR9.Qei6eOCuxJb0oh734kW6uY960bw0NRrnT9p1uTxUELI',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYyMDI3OTQ1LCJpYXQiOjE2NjE0MjMxNDUsImp0aSI6IjJlYWY2MjMyY2ZmMzRkYmViYTM1ZDg3MzYzYzk0NWUwIiwidXNlcl9pZCI6MTR9.Qei6eOCuxJb0oh734kW6ukA913AKqRrnT9p1uTx19Ok'
    }
    ```

- api/token/
    - POST: returns user's token if user exists. Example body:
    ```
    {
        "username": "MyName",
        "password": "MySecret123!"
    }
    ```
    Example of json returned
    ```
    {
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYyMDI4MTQxLCJpYXQiOjE2NjE0MjMzNDEsImp0aSI6IjM0ODFmMmVjMzc2MDRjZmM4NGM2MTMwZmRlY2QxMTlhIiwidXNlcl9pZCI6MTV9.knR-rPlLazTKQtgoBT9loWRc-gLAkqSO4kVyN4bh8Ns',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2MTUwOTc0MSwiaWF0IjoxNjYxNDIzMzQxLCJqdGkiOiJlYTcxMGRkMTg0YWY0Nzk2OTY1N2E4MGUyZjFlYzFhNCIsInVzZXJfaWQiOjE1fQ.KNdp6dpnRnjZ-vOKnari96Cabvoe34g-yot34Ov2SbI'
    }
    ```

### Quiz

- api/quizes/
    - GET returns the user's list of quizes together with the amount. Requires user privilege (given with token). Example return json:
    ```
    {'count': 1, 'data': [
        {'id': 74,
        'title': 'Algebra small quiz 4',
        'alphanumeric_code': '192af5',
        'user': 3,
        'is_published': False,
        'questions': [
            {'question': 'What is 1 + 1?', 'is_multiple_answers': False,
            'answers': [{'answer': '1', 'is_correct': False}, {'answer': '2', 'is_correct': True}, {'answer': '3', 'is_correct': False}]},
            {'question': 'What is 1 + 2?', 'is_multiple_answers': False,
            'answers': [{'answer': '1', 'is_correct': False}, {'answer': '2', 'is_correct': False}, {'answer': '3', 'is_correct': True}]}
            ]
        }
    ]}
    ```
    - POST creates a quiz. Requires user privilege. is_published is False by default but can be true. Example body:
    ```
    [
        {'title': 'Algebra small quiz 4',
        'is_published': False,
        'questions': [
            {'question': 'What is 1 + 1?', 'is_multiple_answers': False, 'id': 1,
            'answers': [{'answer': '1', 'is_correct': False}, {'answer': '2', 'is_correct': True}, {'answer': '3', 'is_correct': False}]},
            {'question': 'What is 1 + 2?', 'is_multiple_answers': False, 'id': 2,
            'answers': [{'answer': '1', 'is_correct': False}, {'answer': '2', 'is_correct': False}, {'answer': '3', 'is_correct': True}]}
            ]
        }
    ]
    ```
        - Checks: If is_published is False, checks are only for data type and non-empty title. If is_published is True, we allow up to 10 questions and 5 answers in each.

- api/quizes/<int:quiz_id>/
    - GET returns the quiz data. Requires user privilege. Example body:
    ```
    {'data': {
        'alphanumeric_code': 'b22261',
        'id': 112,
        'is_published': False,
        'questions': [],
        'title': 'new quiz title',
        'user': 1
    }
    }
    ```
    - PUT edits the quiz if it exists. Requires user privilege. Example body:
    ```
    {'is_published': True}
    ```
    - DELETE deletes the quiz if it exists. Requires user privilege.


## Playing published quiz

- api/play/<str:quiz_alphanumeric_code>/
    - GET returns the information of the published quiz to play. No authorization required. Example body.
    ```
    {
        'data': {
            'alphanumeric_code': 'b22261',
            'id': 112,
            'is_published': True,
            'questions': [
                {
                    'question': 'question 1',
                    'answers': [
                        {'answer': "answer 1"},
                        {'answer': 'answer 2'},
                        {'answer': 'answer 3'}
                    ],
                    'is_multiple_answers': True
                }
            ],
            'title': 'new quiz title',
            'user': 1
        }
    }
    ```
    - POST receives the answers and returns correct answers. The format for each answer is a list of selected options indexes. Example body:
    ```
    {
        'answers': [
            [0, 1],
            [1],
            [0, 2]
        ]
    }
    ```
    Example json returned:
    ```
    {'data': {'correct': 1}}
    ```

## Questions

- api/quizes/<int:quiz_id>/questions/
    - POST creates a new question in a specific quiz. Requires user privileges and owning the quiz.. Example body:
    ```
    {
        'question': 'Question text?',
        'is_multiple_answers': True
    }
    ```
    - GET returns the list of questions. Requires use privileges and owning the quiz. Example json return:
    ```
    {
        'data': [
            {'question': 'Question text?', 'id': 1, 'is_multiple_answers': True, 'answers': []},
            {'question': 'Question text?', 'id': 2, 'is_multiple_answers': True, 'answers': []}
        ]
    }
    ```

- api/quizes/<int:quiz_id>/questions/<int:question_id>/
    - PUT edits the question. Requires user privileges.

    - DELETE deletes question from quiz (and from database). Requires user privileges.

    - GET returns the question. Requires user privileges

- api/quizes/<int:quiz_id>/questions/<int:question_id>/answers/
    - DELETE delets all existent answers in the given question. Requires user privileges.

## Preview of unpublished quiz

- api/preview/<str:quiz_alphanumeric_code>/
    - GET works the same way as GET to 'api/play/<str:quiz_alphanumeric_code>/' but requires user privileges and the quiz must be owned by user.

## Test API

To test endpoints, go to src/ and run:
```
python3 manage.py test app/test/
```
You should see 22 tests passing. More tests can be added in this folder.

# WebApp

## Project setup
Same 'runserver' as above already serves the urls

## Urls:

- http://127.0.0.1:8000/login
    - To login or register

- http://127.0.0.1:8000/dashboard/
    - To see your list of quizes (if logged in). Quiz title can be edited here, and quizes can be removed here.

- http://127.0.0.1:8000/dashboard/1/
    - To see and edit the questions and answers of a quiz. Quiz can be published here.

- http://127.0.0.1:8000/play/b22261/
    - To play a published quiz

- http://127.0.0.1:8000/preview/b22261/
    - To see an unpublished quiz owned by you, the way it would be seen if played

## Setup to test and see

- To create a database from scratch with users {testing1, pass1} and {testing2, pass2}, go to src and run:
```
python3 app/test/script_adding_objects_to_db.py
```