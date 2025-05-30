class TruckNotFoundError(Exception):
    """ Самосвал не найден """
    pass


class TruckModelNotFoundError(Exception):
    """ Модель самосвала не найдена """
    pass


class DuplicateBoardNumberError(Exception):
    """ Бортовой номер уже существует """
    pass