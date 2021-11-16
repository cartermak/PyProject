import json
from typing import Dict, List
from uuid import uuid4
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import date, timedelta


class __PlanObjectType(Enum):
    TASK = auto()
    MILESTONE = auto()
    CATEGORY = auto()


class __PlanObject(ABC):
    def __init__(self, name: str):
        self.id = str(uuid4())
        self.name = name

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type.name}

    @property
    @abstractmethod
    def type(self) -> __PlanObjectType:
        pass


class __Category(__PlanObject):
    def __init__(self, name, children=None) -> None:
        super().__init__(name)
        self.children = [] if children is None else children

    def add_child(self, child: __PlanObject) -> None:
        self.children.append(child)

    @property
    def type(self):
        return __PlanObjectType.CATEGORY

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['children'] = [c.to_dict() for c in self.children]
        return data


class __Task(__PlanObject):
    def __init__(self, name: str, start: date, duration: timedelta, margin: timedelta = None):
        super().__init__(name)
        self.start = start
        self.duration = duration
        self.margin = timedelta(0) if margin is None else margin

    @property
    def type(self) -> __PlanObjectType:
        return __PlanObjectType.TASK

    def to_dict(self):
        data = super().to_dict()
        data['start'] = str(self.start)
        data['duration'] = str(self.duration)
        data['margin'] = str(self.margin)
        return data


class __Milestone(__PlanObject):
    def __init__(self, name: str, target_date: date):
        super().__init__(name)
        self.target_date = target_date

    @property
    def type(self) -> __PlanObjectType:
        return __PlanObjectType.MILESTONE

    def to_dict(self):
        data = super().to_dict()
        data['target_date'] = str(self.target_date)
        return data


class __Project():
    def __init__(self, name: str, data: List[__PlanObject] = None) -> None:
        self.name = name
        self.data = [] if data is None else data

    def to_dict(self):
        return {self.name: [d.to_dict() for d in self.data]}
