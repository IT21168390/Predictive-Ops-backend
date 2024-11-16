from flask_pymongo import PyMongo

mongo = PyMongo()

class Instructions:
    def __init__(self, failure, details):
        self.failure = failure
        self.detalis = details