from typing import cast

from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship

from ._base import BaseModel


class ModelTruck(BaseModel):
    """ Модель самосвала """
    __tablename__ = "truck_models"

    name = Column(String, unique=True, nullable=False, comment="Название модели")
    max_capacity = Column(Integer, nullable=False, comment="Максимальная грузоподъемность (тонн)")

    trucks = relationship("DumpTruck", back_populates="model")

    def __repr__(self):
        return f"<Модель {self.name}, макс грузоподъемность {self.max_capacity}>"


class DumpTruck(BaseModel):
    """ Параметры конкретного самосвала """
    __tablename__ = "dump_trucks"

    board_number = Column(String, unique=True, nullable=False, comment="Бортовой номер")
    current_weight = Column(Integer, nullable=False, comment="Текущий вес груза (тонн)")

    model_id = Column(Integer, ForeignKey("truck_models.id"), nullable=False)

    model = relationship(ModelTruck, back_populates="trucks")

    def __repr__(self):
        return f"<Самосвал с бортовым номером {self.board_number} и текущей загрузкой {self.current_weight}>"

    @property
    def load_percentage(self) -> float:
        """ Вычисляет процент загрузки от максимальной грузоподъемности """

        # аннотации типов для IDE, чтобы избежать предупреждений о некорректном типе данных
        truck_model = cast(ModelTruck, self.model)

        max_capacity = cast(int, truck_model.max_capacity)
        current_weight = cast(int, self.current_weight)

        if max_capacity > 0:
            return max(round((current_weight / max_capacity) * 100, 2), 0)
        return 0

    @property
    def is_overloaded(self) -> bool:
        """ Проверяет, перегружен ли самосвал """
        return self.load_percentage > 100
