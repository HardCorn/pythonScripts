class TesterException(BaseException):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ': '.join(self.args)


class TemplateLinkerError(TesterException):
    pass


class ScriptGeneratorError(TesterException):
    pass


class TemplateSQLGeneratorError(TesterException):
    pass


class ScriptReaderException(TesterException):
    pass


class EOF(ScriptReaderException):
    pass