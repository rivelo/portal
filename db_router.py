# -*- coding: utf-8 -*-

class DBRouter(object):
    """
    Docs: https://docs.djangoproject.com/en/1.9/topics/db/multi-db/#an-example
    A router to control all database operations on models in the
    auth application.
    $ ./manage.py migrate
    $ ./manage.py migrate --database=other_db
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to 'other_db'.
        """
        if model._meta.app_label == 'accounting':
            return 'catalog'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to 'other_db'.
        """
        if model._meta.app_label == 'accounting':
            return 'catalog'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'accounting' or \
           obj2._meta.app_label == 'accounting':
            return True
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'other_db'
        database.
        """

        if app_label == 'accounting':
            return db == 'catalog'
        return 'default'


class CatalogRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'accounting':
            return 'catalog'
        return None
    # same for write

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'accounting':
            return 'catalog'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'accounting' or \
           obj2._meta.app_label == 'accounting':
           return True
        return None

    def allow_migrate(self, db, model):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if db == 'auth_db':
            return model._meta.app_label == 'accounting'
        elif model._meta.app_label == 'accounting':
            return False
        return None

    def allow_syncdb(self, db, model):
        if db == 'catalog':
            return model._meta.app_label == 'accounting'
        elif model._meta.app_label == 'accounting':
            return False
        return None


class OtherRouter(object):
    def db_for_read(self, model, **hints):
        return "default"
    # same for write, relation, syncdb

    def db_for_write(self, model, **hints):
        return "default"
    
    