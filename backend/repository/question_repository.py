import json

from sqlalchemy import func

from domain import Question, QuestionType

from datetime import datetime


def get_question_by_id(session, question_id):
    """
    search question by question id
    :return: question object
    """
    question = session.query(Question).filter(Question.id == question_id).first()
    if question and question.status == 1:
        # We need to use the object after this session closed
        session.expunge(question)
        # delete reason content in choice (not displayed when getting questions)
        choice = json.loads(question.choice)
        for row in choice:
            row.pop('reason')
        print(choice)
        question.choice = choice
        return question
    else:
        return None


def get_question_list(session, num):
    """
    get random questions
    :param session:
    :param num: number of questions
    :return: question list
    """
    questions = session.query(Question).order_by(func.random()).limit(num).all()
    session.expunge_all()
    # delete reason content in choice (not displayed when getting questions)
    for question in questions:
        choice = json.loads(question.choice)
        for choice_row in choice:
            choice_row.pop('reason')
        question.choice = choice
    return questions


def create_question(session, question_type, role, description, choice, difficulty, answer):
    """
    create a new question
    :param session:
    :param question_type:
    :param role:
    :param description:
    :param choice:
    :param difficulty:
    :param answer
    :return: returns id of the new question
    """
    question = Question(question_type=question_type, role=role, description=description, choice=choice,
                        difficulty=difficulty, answer=answer)
    session.add(question)
    session.flush()
    return question.id


def delete_question(session, question_id):
    """
    delete a question
    :param session:
    :param question_id: id of the question want to delete
    :return: True: delete successful
             False: delete successful
    """
    existing = session.query(Question).filter(id=question_id).first()
    if existing is not None:
        session.delete(existing)
        session.flush()
        return True
    return False


def update_question(session, question_id, description, choice, difficulty, answer):
    """
    update a question
    :param session:
    :param question_id:
    :param description:
    :param choice:
    :param difficulty:
    :param answer:
    """
    question = session.query(Question).filter(id=question_id).first()
    if description is None:
        description = question.description
    if choice is None:
        choice = question.choice
    if difficulty is None:
        difficulty = question.choice
    if answer is None:
        answer = question.choice
    question.description = description
    question.choice = choice
    question.difficulty = difficulty
    question.answer = answer
    question.update_time = datetime.now()


def check_answer(session, question_id, answer):
    """
    check the answer
    :param session:
    :param question_id:
    :param answer: one character, e.g: A/B/C/D...
    :return:
    """
    question = session.query(Question).filter(id=question_id).first()
    if question.answer == answer:
        return True
    return False

