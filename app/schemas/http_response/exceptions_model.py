class ModelNotFoundError(Exception):
    """ Модель не найдена """
    pass


class DuplicateModelNameError(Exception):
    """ Модель с таким именем уже существует """
    pass