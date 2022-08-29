import os
from flask import Flask, request, abort, jsonify
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
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTION')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        current_categories = paginate_questions(request, categories)
        if len(current_categories) == 0:
            abort(404)
        else:
            formatted_categories = current_categories
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'totals_categories': len(Category.query.all())
            })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def paginate_questions(request, selection):
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)
            
            categories = Category.query.all()
            categories_list = {}

            for req in categories:
                categories_list[req.id] = req.type

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories_list
                
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).delete()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": current_questions,
                "total_questions": len(Question.query.all())
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions/create', methods=['POST'])
    def new_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "created": question.id,
                "questions": current_questions,
                "total_questions": len(Question.query.all())
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_term_questions():
        body = request.get_json()
        search = body.get('search', None)

        if search:
            questions = Question.query.order_by(Question.id).filter(
                Question.category.ilike('%{}%'.format(search)))
            current_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'totals_questions': len(questions)
            })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is None:
            abort(404)
        try:
            questions = Question.query.filter_by(category=category.id).all()
            current_questions = paginate_questions(request, questions)
            question = len(Question.query.all())

            return jsonify({
                'success': True,
                'total_questions': question,
                'current_category': category.type,
                'questions': current_questions
            })

        except:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/questions', methods=['POST'])
    def play_quiz_questions():

        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)

            category_id = category['id']
            pass_next_question = None
            
            if category_id is not None:
                get_questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous_questions))).all()    
            else:
                get_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
            
            if len(get_questions) > 0:
                pass_next_question = random.choice(get_questions).format()
            
            return jsonify({
                'question': pass_next_question,
                'success': True,
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.error_handler(400)
    def bad_Request(error):
        return (jsonify({
            'success': False,
            'error': 400,
            'message': 'bad Request'
        }), 400)

    @app.error_handler(404)
    def not_found(error):
        return (jsonify({
            'success': False,
            'error': 404,
            'message': ' ressource not found'
        }), 404)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405)

    @app.error_handler(422)
    def Unprocessable(error):
        return (jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422)

    @app.error_handler(500)
    def Server_Error(error):
        return (jsonify({
            'success': False,
            'error': 500,
            'message': 'Server_Error'
        }), 500)

    return app