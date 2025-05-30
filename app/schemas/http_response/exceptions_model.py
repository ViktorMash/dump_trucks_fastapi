class ModelNotFoundError(Exception):
    """Исключение когда модель не найдена"""
    pass


class DuplicateModelNameError(Exception):
    """Исключение когда модель с таким именем уже существует"""
    pass