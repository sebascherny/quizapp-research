import uuid
from rest_framework.decorators import api_view
from django.shortcuts import HttpResponse
from rest_framework import status
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from app.models import Quiz
import json

def get_question_errors(question):
    errors = []
    is_multiple_answers = question.get("is_multiple_answers")
    if not question.get("question"):
        errors.append({"question": "Question is required"})
    if not question.get("answers"):
        errors.append({"answers": "At least one answer is required"})
    elif len(question.get("answers")) > 5:
        errors.append({"answers": "Questions must have up to 5 answers"})
    else:
        correct_answers = len([answer for answer in question["answers"] if answer.get("correct")])
        if any(not answer.get("answer") for answer in question["answers"]):
            errors.append({"answers": "Answers must be non empty"})
        if correct_answers == 0:
            errors.append({"answers": "At least one answer must be correct"})
        if correct_answers > 1 and not is_multiple_answers:
            errors.append({"answers": "If question is one-answer only, just one answer should be correct"})
    return errors
            

def check_and_get_errors_before_publishing(questions):
    errors = []
    if not questions:
        errors.append({"length": "Quiz must have up at least one question to be published"})
    elif len(questions) > 10:
        errors.append({"length": "Quiz must have up to 10 questions to be published"})
    else:
        all_questions_errors = {}
        for i, question in enumerate(questions):
            question_errors = get_question_errors(question)
            if question_errors:
                all_questions_errors[i] = question_errors
        if all_questions_errors:
            errors.append({"questions": all_questions_errors})
    return errors

def serialize_quiz(quiz):
    serialized = model_to_dict(quiz)
    if not serialized["questions"]:
        serialized["questions"] = []
    return serialized

def serialize_quiz_to_play(quiz):
    serialized = serialize_quiz(quiz)
    for question in serialized["questions"]:
        question["answers"] = [{"answer": answer["answer"]} for answer in question["answers"]] # Hide 'correct' field
    return serialized

def _get_unique_randomized_alphanumeric_code():
    code = str(uuid.uuid4()).replace("-", "")[:6]
    while len(Quiz.objects.filter(alphanumeric_code=code)):
        code = str(uuid.uuid4()).replace("-", "")[:6]
    return code

def get_data_type_errors(questions, is_published):
    errs = []
    if not isinstance(is_published, bool):
        errs.append({"is_published": "Must be either true or false, instead it is {}".format(is_published)})
    if not questions:
        return errs
    if not isinstance(questions, list):
        errs.append({"questions": "Questions must be a list"})
    else:
        for question in questions:
            if not isinstance(question, dict):
                errs.append({"questions": "Each question must be a dictionary"})
                break
            forbidden_keys = [k for k in question if k not in ("question", "is_multiple_answers", "answers")]
            if forbidden_keys:
                errs.append({"questions": "The following keys should not be given: {}".format(forbidden_keys)})
                break
            if "question" in question and not isinstance(question["question"], str):
                errs.append({"questions": "The questions should be text"})
                break
            if 'is_multiple_answers' in question and not isinstance(question['is_multiple_answers'], bool):
                errs.append({"questions": "Field 'is_multiple_answers' should be boolean"})
                break
            if 'answers' in question and not isinstance(question['answers'], list):
                errs.append({"questions": "Field 'answers' should be a list"})
                break
            for answer in question.get("answers", []):
                if not isinstance(answer, dict):
                    errs.append({"answers": "Answers should be a list of dictionaries"})
                    break
                forbidden_keys = [k for k in answer if k not in ("answer", "correct")]
                if forbidden_keys:
                    errs.append({"answers": "The following keys should not be given in answer: {}".format(forbidden_keys)})
                    break
                if "answer" in answer and not isinstance(answer["answer"], str):
                    errs.append({"answers": "The answers should be text"})
                    break
                if 'correct' in question and not isinstance(answer['correct'], bool):
                    errs.append({"answers": "Field 'correct' should be boolean"})
                    break
    return errs

def save_quiz(request, quiz, success_status):
    errors = []
    questions = request.data.get("questions")
    title = request.data.get("title", None)
    is_published = request.data.get("is_published") or False
    
    if quiz.id and quiz.is_published:
        # Allowing published quiz to be unpublished
        if is_published or title or questions:
            errors = [{"published_quiz": "First unpublish the quiz and then you will be able to edit it"}]
    
    if not errors:
        if quiz.id:
            if title is None:
                title = quiz.title
            if questions is None:
                questions = quiz.questions
            if is_published is None:
                is_published = quiz.is_published
        if len(title) == 0:
            errors.append({"title": "This field is required"})
        errors.extend(get_data_type_errors(questions, is_published))
        if is_published and not errors:
            errors.extend(check_and_get_errors_before_publishing(questions))

    if len(errors) > 0:
        return HttpResponse(json.dumps(
            {
                "errors": errors
            }), status=status.HTTP_400_BAD_REQUEST)

    try:
        quiz.alphanumeric_code = quiz.alphanumeric_code or _get_unique_randomized_alphanumeric_code()
        quiz.title = title
        quiz.questions = questions or []
        quiz.user = request.user
        quiz.is_published = is_published
        quiz.save()
    except Exception as e:
        return HttpResponse(json.dumps(
            {
                "errors": {"Quiz": str(e)}
            }), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"data": serialize_quiz(quiz)}), status=success_status)


@api_view(['GET', 'POST'])
def quizes(request):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        quizes_data = Quiz.objects.filter(user=request.user)

        quizes_count = quizes_data.count()

        page_size = int(request.GET.get("page_size", "10"))
        page_no = request.GET.get("page_no")
        if page_no:
            page_no = int(page_no)
            quizes_data = list(quizes_data[page_no * page_size:page_no * page_size + page_size])

        quizes_data = [serialize_quiz(quiz) for quiz in quizes_data]
        return HttpResponse(json.dumps({"count": quizes_count, "data": quizes_data}), status=status.HTTP_200_OK)

    if request.method == "POST":
        quiz = Quiz()
        return save_quiz(request, quiz, status.HTTP_201_CREATED)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', 'PUT', 'DELETE'])
def quiz(request, quiz_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    if request.user != quiz.user:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_quiz(quiz)}), status=status.HTTP_200_OK)

    if request.method == "PUT":
        return save_quiz(request, quiz, status.HTTP_200_OK)

    if request.method == "DELETE":
        quiz.delete()
        return HttpResponse(json.dumps({"detail": "deleted"}), status=status.HTTP_410_GONE)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)

def check_answers(request, quiz):
    answers = request.data.get("answers")
    if (answers is None) or (not isinstance(answers, list)) or len(answers) != len(quiz.questions):
        return {"success": False, "data": {"message": "You should send a list of answers, one per question"}}
    result = 0
    for i in range(len(answers)):
        given_answer = answers[i]
        should_be_answer = [j for j, option in enumerate(quiz.questions[i]["answers"]) if option["correct"]]
        if sorted(given_answer) == should_be_answer:
            result += 1
    return {"success": True, "data": {"correct": result}}

@api_view(['GET', 'POST'])
def play(request, quiz_alphanumeric_code):
    try:
        quiz = Quiz.objects.get(alphanumeric_code=quiz_alphanumeric_code, is_published=True)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)
    except MultipleObjectsReturned:
        return HttpResponse(json.dumps({"detail": "Something weird happened"}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_quiz_to_play(quiz)}), status=status.HTTP_200_OK)

    if request.method == "POST":
        result = check_answers(request, quiz)
        if result["success"]:
            return HttpResponse(json.dumps({"data": result["data"]}), status=status.HTTP_200_OK if result["success"] else status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(json.dumps({"detail": result["data"]}), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
def preview(request, quiz_alphanumeric_code):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        quiz = Quiz.objects.get(alphanumeric_code=quiz_alphanumeric_code)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)
    except MultipleObjectsReturned:
        return HttpResponse(json.dumps({"detail": "Something weird happened"}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.user != quiz.user:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_quiz_to_play(quiz)}), status=status.HTTP_200_OK)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)
