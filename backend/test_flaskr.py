import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:1516@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        """
        test pour la recuperation des cateories
        """
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    
    def test_get_questions(self):
        """
        test pour la recuperation des questions
        """
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    
    def test_get_questions_404(self):
        """
        test avec de faux parametres
        """
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question_422(self):   
        """
        test de suppression avec un mauvais id
        """
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)

    
    
    def test_create_question(self):
        """
        test de creation de questions
        """
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    
    def test_405_question(self):
        """
        test de l'erreur 405
        """
        response = self.client().post('/questions/65', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    

    def test_get_questions_by_category(self):
        """
        test de recuperation d'une categorie selon son id
        """
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['current_category'], 'Science')
        self.assertEqual(data['success'], True)

    
    def test_get_404_questions_by_category(self):
        """
        test de recuperation d'une ressource qui n'existe pas
        """
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    
    def test_play_quiz(self):
        new_quiz = {'previous_questions': [],
                            'quiz_category': {'type': 'Entertainment', 'id': 2}}

        res = self.client().post('/questions', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    
    def test_404_play_quiz(self):
        new_quiz = {'previous_questions': []}
        res = self.client().post('/questions', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
    if __name__ == "__main__":
         unittest.main()