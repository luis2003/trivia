import os
from flask import Flask, request, abort, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO-DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO-DONE: Use the after_request decorator to set Access-Control-Allow
  '''

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO-DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()

    if len(categories) == 0:
      abort(404)

    catgs_dict = {cat.id: cat.type for cat in categories}

    return jsonify({
      'categories': catgs_dict
    })

  '''
  @TODO-DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST-DONE: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.id).all()
    catgs_dict = {cat.id: cat.type for cat in categories}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'questions': current_questions,
      'total_questions': len(Question.query.all()),  # should this not be len of selection?
      'current_category': None,
      'categories': catgs_dict
    })
  '''
  @TODO-DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST-DONE: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete_question(q_id):
    try:
      q_to_delete = Question.query.filter(Question.id == q_id).one_or_none()

      if q_to_delete is None:
        abort(404)

      q_to_delete.delete()

      return jsonify({
        'success': True,
      })

    except:
      abort(422)

  '''
  @TODO-DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST-DONE: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_or_search_questions():
    body = request.get_json()

    for value in body:
        if value == "":
          abort(422)

    new_q_question = body.get('question', None)
    new_q_answer = body.get('answer', None)
    new_q_difficulty = body.get('difficulty', None)
    new_q_category = body.get('category', None)
    search = body.get('searchTerm', None)

    if not search:
      if (not new_q_question or
        not new_q_question or
        not new_q_difficulty or
        not new_q_category):
        abort(422)

    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        select_result = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        catgs_dict = {cat.id: cat.type for cat in categories}

        if len(select_result) == 0:
          abort(404)

        return jsonify({
          'questions': select_result,
          'total_questions': len(Question.query.all()),  # should this not be len of selection?
          'current_category': None,
          'categories': catgs_dict
        })

      else:
        new_q = Question(question=new_q_question,
                         answer=new_q_answer,
                         difficulty=new_q_difficulty,
                         category=new_q_category)

        new_q.insert()

        return jsonify({
          'success': True
        })

    except:
      abort(422)
  '''
  @TODO-DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST-DONE: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
# see  @app.route('/questions', methods=['POST'])
  '''
  @TODO-DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST-DONE: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def retrieve_questions_by_category(cat_id):

    selection = Question.query.order_by(Question.id).filter(Question.category == cat_id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.id).all()
    catgs_dict = {cat.id: cat.type for cat in categories}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': None,
      'categories': catgs_dict
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def retrieve_questions_for_quiz():
    pass

  '''
  @TODO-DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method Not Allowed"
      }), 405

  @app.errorhandler(422)
  def  unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": " Unprocessable Entity"
      }), 422

  return app

    