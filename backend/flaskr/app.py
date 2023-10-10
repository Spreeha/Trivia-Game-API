import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from flask_migrate import Migrate

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

"""
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
"""

"""
    @TODO: Use the after_request decorator to set Access-Control-Allow
"""

def create_app(db_URI="",test_config=None):
    # create and configure the app
    # app = Flask(__name__)
    # setup_db(app)
    app = Flask(__name__, instance_relative_config=True)
    with app.app_context():
        if db_URI:
            setup_db(app,db_URI)
        else:
            setup_db(app)
        # setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    
    @app.route('/categories')
    def get_categories():
        '''
        Handles GET requests for getting all categories.
        '''
        categories = Category.query.all()
        dict_of_categories = dict()

        for category in categories:
            dict_of_categories[category.id] = category.type

        if len(dict_of_categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": dict_of_categories,
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
    
    @app.route('/questions')
    def get_questions():
        '''
        Handles GET requests for getting all questions.
        '''
        questions = Question.query.all()
        num_of_ques = len(questions)
        ques_on_current_page = paginate_questions(request, questions)

        categories = Category.query.all()
        dict_of_categories = dict()

        for category in categories:
            dict_of_categories[category.id] = category.type

        if len(ques_on_current_page) == 0:
            abort(404)

        # currentCategoryType = Category.query.filter(ques_on_current_page['category']).one_or_none()
        # currentCategory = currentCategoryType.type
        currentCategory = 'History'

        return jsonify({
            "success": True,
            "questions": ques_on_current_page,
            "totalQuestions": num_of_ques,
            "categories": dict_of_categories,
            # "currentCategory": currentCategory,
        })
    
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods = ['DELETE'])
    def delete_question(id):
        '''
        Handles DELETE requests for deleting a question by id.
        '''
        print("Inside deleting question")
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            print("Ques is ",question.question)
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                "success": True,
                "deleted": id,
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

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions',methods=['POST'])
    def create_question():
        '''
        Handles POST requests for creating new questions and searching questions.
        '''
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        searchTerm = body.get('searchTerm', None)
        
        
        try:
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                )
                current_questions = paginate_questions(request, selection)
                totalQuestions = len(current_questions)
                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": totalQuestions,
                })
            
            else:
                if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
                    abort(422)
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    "success": True,
                    'ques_id': question.id,
                    'created_question': question.question,
                    'questions': current_questions,
                    'totalQuestions': len(Question.query.all())
                })
            
        except:
            abort(422)

    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def get_ques_by_categories(id):
        '''
        Handles GET requests for getting questions based on category.
        '''
        category = Category.query.filter_by(id=id).one_or_none()
        if category is None:
            abort(400)
        questions_selection = Question.query.filter_by(category = str(category.id)).all()
        current_ques = paginate_questions(request, questions_selection)

        return jsonify({
            "success": True,
            "questions": current_ques,
            "totalQuestions": len(Question.query.all()),
            "currentCategory": category.type,
        })
    

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

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
        '''
        Handles POST requests for playing quiz.
        '''
        body = request.get_json()
        prev_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        category = Category.query.filter_by(type = quiz_category).one_or_none()
        # print('Type is ',category.type)

        if prev_questions is None or quiz_category is None:
            abort(400)

        # print('ID of selected category is ',category.id)
        # print('Type of category ID is ',type(category.id))
        if int(category.id) == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category = str(category.id)).all()

        def get_random_ques():
            return questions[random.randrange(0, len(questions), 1)]
        
        def check_used_ques(question):
            used = False
            if question.id in prev_questions:
                used = True
            return used
        
        question = get_random_ques()

        while(check_used_ques(question)):
            question = get_random_ques()
            if(len(prev_questions)==len(questions)):
                return jsonify({
                    "success": True,
                })
            
        return jsonify({
            'success': True,
            'question': question.format(),
        })
    

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    
    @app.errorhandler(415)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 415,
            "message": "unsupported content type"
        }), 415
    
    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405


    return app

