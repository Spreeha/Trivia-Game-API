import os
import unittest
import json

from app import create_app
from models import setup_db, Question, Category

# app = create_app()  # Initialize the Flask app here
# database_name = "bookshelf_test"
# database_path = 'postgresql://postgres:root@localhost:5432/bookshelf_test'
# setup_db(app, database_path)  # Initialize the database once

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    # @classmethod
    # def setUpClass(cls):
    #     """Executed once before all tests. Initialize the app and database here."""
    #     cls.app = create_app()
    #     cls.client = cls.app.test_client()
    #     cls.database_name = "bookshelf_test"
    #     cls.database_path = 'postgresql://postgres:root@localhost:5432/bookshelf_test'
    #     with cls.app.app_context():
    #         setup_db(cls.app, cls.database_path)

    # @classmethod
    # def tearDownClass(cls):
    #     """Executed once after all tests. Close the database and clean up here."""
    #     pass

    def setUp(self):
        """Define test variables and initialize app."""
        
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:root@localhost:5432/trivia'

        self.app = create_app(self.database_path)
        self.client = self.app.test_client
        # with self.app.app_context():
        #     setup_db(self.app, self.database_path)
        
        self.new_question = {
            "question": "What is the capital of India?", 
            "answer": "New Delhi", 
            "category": 4,
            "difficulty": 3
            }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        """Tests question pagination success"""
        res = self.client().get("/questions")
        data = json.loads(res.data)
        # print("JSON response data is ", data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        """Tests question pagination failure 404"""
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        # print("JSON response data is ", data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_categories(self):
        """Tests fetching of categories success"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    # def test_delete_question(self):
    #     """Tests question deletion success"""
    #     with self.app.app_context():
    #         res = self.client().delete("/questions/11")
    #         data = json.loads(res.data)

    #         question = Question.query.filter(Question.id == 11).one_or_none()

    #         self.assertEqual(res.status_code, 200)
    #         self.assertEqual(data["success"], True)
    #         self.assertEqual(data["deleted"], 11)
    #         self.assertEqual(question, None)

    
    # def test_create_question(self):
    #     """Tests question creation success"""
    #     res = self.client().post("/questions", json=self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["created_question"])
    #     self.assertTrue(len(data["questions"]))


    def test_422_if_question_creation_fails(self):
        """Tests question creation failure 422"""
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_get_book_search_with_results(self):
        """Tests search questions success"""
        res = self.client().post("/questions", json={"searchTerm": "Which"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        # self.assertEqual(len(data["questions"]), 1)

    def test_get_book_search_without_results(self):
        """Tests search questions failure 404"""
        res = self.client().post("/questions", json={"searchTerm": "applejacks"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        # self.assertEqual(len(data["questions"]), 0)

    def test_ques_by_categories(self):
        '''Test fetching questions category wise'''
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["currentCategory"], 'History')
        self.assertNotEqual(len(data['questions']), 0)

    def test_failure_of_get_ques_by_categories(self):
        '''Tests failure of getting questions by categories'''
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'bad request')


    def test_get_random_quiz_ques(self):
        '''Tests getting random questions for playing the quiz'''
        res = self.client().post("/quizzes", json = {"previous_questions":[5,9,23], "quiz_category":"History"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'],9)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
