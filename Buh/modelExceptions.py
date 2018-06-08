import utility


class BaseModelException(utility.BaseError):
    pass


class ModelViewException(BaseModelException):
    pass


class ModelTemplateException(BaseModelException):
    pass


class ModelManagerException(BaseModelException):
    pass


class FilterException(BaseModelException):
    pass


class ModelMetaException(BaseModelException):
    pass


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


class Stopper(BaseModelException):
    pass


class StopArithmetic(Stopper):
    pass


class StopBool(Stopper):
    pass


class StopControl(Stopper):
    pass