from flask import current_app
from flask_testing import TestCase
from project import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        test_uri = 'mysql+pymysql://root:root321@users-db:3306/users_dev'
        self.assertTrue(app.config['SECRET_KEY'] == 'secret')
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == test_uri)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_development(self):
        test_uri = 'mysql+pymysql://root:root321@users-db:3306/users_test'
        self.assertTrue(app.config['SECRET_KEY'] == 'secret')
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == test_uri)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'secret')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
