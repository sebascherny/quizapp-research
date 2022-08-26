import uuid
from rest_framework.decorators import api_view
from django.shortcuts import HttpResponse
from rest_framework import status
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from app.models import Answer, Question, Quiz
import json

def serialize_answer(ans_obj):
    return {"answer": ans_obj.answer, "is_correct": ans_obj.is_correct, "id": ans_obj.id}

def serialize_question(q_obj):
    answers_objs = Answer.objects.filter(question=q_obj) or []
    return {"question": q_obj.question, "id": q_obj.id,
            "is_multiple_answers": q_obj.is_multiple_answers,
            "answers": [serialize_answer(ans_obj) for ans_obj in answers_objs]}

def serialize_quiz(quiz):
    serialized = model_to_dict(quiz)
    q_objs = Question.objects.filter(quiz=quiz) or []
    serialized["questions"] = [serialize_question(question) for question in q_objs]
    return serialized

def save_question(request, q_obj, quiz_obj, success_status):
    answers = request.data.get("answers")
    question = request.data.get("question", None)
    is_multiple_answers = request.data.get("is_multiple_answers")
    
    errors = []
    if q_obj.id:
        if question is None:
            question = q_obj.question
        if is_multiple_answers is None:
            is_multiple_answers = q_obj.is_multiple_answers
    if is_multiple_answers is None:
        # default value
        is_multiple_answers = False
    if question is not None:
        if not isinstance(question, str):
            errors.append({"question": "This field must be string"})
    if answers is not None:
        if not isinstance(answers, list):
            errors.append({"answers": "This field must be a list"})
        else:
            for answer in answers:
                if not isinstance(answer, dict):
                    errors.append({"answers": "Each answer in the list must be a dict"})
                else:
                    if "is_correct" in answer and not isinstance(answer["is_correct"], bool):
                        errors.append({"is_correct": "This field must be boolean"})
                    if "answer" in answer and not isinstance(answer["answer"], str):
                        errors.append({"answer": "This field must be string"})
    if len(errors) > 0:
        return HttpResponse(json.dumps(
            {
                "errors": errors
            }), status=status.HTTP_400_BAD_REQUEST)

    try:
        q_obj.quiz = quiz_obj
        q_obj.question = question
        q_obj.is_multiple_answers = is_multiple_answers
        q_obj.save()
        if answers == []:
            for ans_obj in Answer.objects.filter(question=q_obj):
                ans_obj.delete()
        for answer in (answers or []):
            if answer.get("id"):
                try:
                    ans_obj = Answer.objects.get(pk=answer["id"])
                    if "answer" in answer:
                        ans_obj.answer = answer["answer"]
                    if "is_correct" in answer:
                        ans_obj.is_correct = answer.get("is_correct", False)
                except ObjectDoesNotExist:
                    continue
            else:
                ans_obj = Answer(question=q_obj)
                ans_obj.answer = answer["answer"]
                ans_obj.is_correct = answer.get("is_correct", False)
            ans_obj.save()
    except Exception as e:
        return HttpResponse(json.dumps(
            {
                "errors": {"Question": str(e)}
            }), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"data": serialize_question(q_obj)}), status=success_status)


@api_view(['GET', 'POST'])
def questions(request, quiz_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)
    if not quiz or quiz.user != request.user:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "POST":
        question = Question()
        return save_question(request, question, quiz, status.HTTP_201_CREATED)
    
    if request.method == "GET":
        questions = Question.objects.filter(quiz=quiz)
        return HttpResponse(json.dumps({"data": [serialize_question(q_obj) for q_obj in questions]}), status=status.HTTP_200_OK)
    
    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET', 'PUT', 'DELETE'])
def question(request, quiz_id, question_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        quiz = Quiz.objects.get(id=quiz_id)
        q_obj = Question.objects.get(id=question_id, quiz=quiz)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)
    if quiz.user != request.user:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "PUT":
        return save_question(request, q_obj, quiz, status.HTTP_200_OK)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_question(q_obj)}), status=status.HTTP_200_OK)
    
    if request.method == "DELETE":
        q_obj.delete()
        return HttpResponse(json.dumps({"detail": "deleted question"}), status=status.HTTP_410_GONE)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['DELETE'])
def answers(request, quiz_id, question_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        quiz = Quiz.objects.get(pk=quiz_id)
        question = Question.objects.get(pk=question_id, quiz=quiz)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    if request.user != quiz.user:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "DELETE":
        answers = Answer.objects.filter(question=question)
        for ans_obj in answers:
            ans_obj.delete()
        return HttpResponse(json.dumps({"detail": "deleted all answers"}), status=status.HTTP_410_GONE)
    
    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)