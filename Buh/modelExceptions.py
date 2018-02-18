class BaseModelException(BaseException):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ':'.join(self.args)


class ModelFileException(BaseModelException):
    pass


class ModelWriteError(ModelFileException):
    pass


class ModelReadError(ModelFileException):
    pass


class ModelModifyError(ModelFileException):
    pass


class DataValidationError(ModelFileException):
    pass


class UtilityException(BaseModelException):
    pass