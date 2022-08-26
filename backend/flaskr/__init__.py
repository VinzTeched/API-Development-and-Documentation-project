import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={"/": {"origins": "*"}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def categories():
        all = Category.query.order_by(Category.id).all()

        if all is None:
            abort(404)

     #  categories = [category.format() for category in all]

        return jsonify(
            {
                "success": True,
                "categories": {categories.id: categories.type for categories in all},
            }
        )


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
    def questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        
        all = Category.query.order_by(Category.id).all()

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "categories": {categories.id: categories.type for categories in all},
                "total_questions": len(Question.query.all()),
                "current_category": "Science"
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            query = Question.query.filter(Question.id==question_id).one_or_none()

            if query is None:
                abort(404)

            query.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)
            
            all = Category.query.order_by(Category.id).all()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "categories": {categories.id: categories.type for categories in all},
                    "total_questions": len(Question.query.all()),
                    "current_category": "Science"
                }
            )

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
    
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )

                current_questions = paginate_questions(request, selection)

                all = Category.query.order_by(Category.id).all()

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "categories": {categories.id: categories.type for categories in all},
                        "total_questions": len(current_questions),
                        "current_category": "Science"
                    }
                )
            else: 
                question  = Question(question=new_question, answer=new_answer, category=category, difficulty=difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                all = Category.query.order_by(Category.id).all()

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "categories": {categories.id: categories.type for categories in all},
                        "total_questions": len(Question.query.all()),
                        "current_category": "Science"
                    }
                )
        except:
            abort(422)



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def category_questions(id):
 
        category = Category.query.filter(Category.id==id).one_or_none()

        if category:
            my_query = Question.query.filter(Question.category==str(id)).all()
            current_questions = paginate_questions(request, my_query)
        
            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(my_query),
                    "current_category": category.type
                }
            )
        else:
            abort(404)


          

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
    def get_quiz():

        # retrieve a new question not already shown
        body = request.get_json()
        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        cat_id = quiz_category['id']

        try:
            if cat_id == 0:
                my_query = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                my_query = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == cat_id).all()
                    
            next_question = None

            if(my_query):
                next_question = random.choice(my_query)
                return jsonify(
                    {
                        'success': True,
                        'question': next_question.format(),
                        'previous_questions': previous_questions
                    }
                )

            else:
                return jsonify(
                    {
                        "success": False
                    }
                )

        except Exception as e:
            print(e)
            abort(404)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

