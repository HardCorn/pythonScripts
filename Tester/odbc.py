import pyodbc


def connect(source):
    return True


def exec_sql(source):
    pass


def select(source):
    return ''


def get_sources():
    return ['td06']
    # return pyodbc.dataSources()


def disconnect(source=None):
    return True
