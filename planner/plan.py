import json
from typing import Dict, List
from uuid import uuid4
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import date, timedelta


class PlanObjectType(Enum):
    TASK = auto()
    MILESTONE = auto()
    CATEGORY = auto()


class PlanObject(ABC):
    def __init__(self, name: str):
        self.id = str(uuid4())
        self.name = name

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type.name}

    @property
    @abstractmethod
    def type(self) -> PlanObjectType:
        pass


class Category(PlanObject):
    def __init__(self, name, children=None) -> None:
        super().__init__(name)
        self.children = [] if children is None else children

    def add_child(self, child: PlanObject) -> None:
        self.children.append(child)

    @property
    def type(self):
        return PlanObjectType.CATEGORY

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['children'] = [c.to_dict() for c in self.children]
        return data


class Task(PlanObject):
    def __init__(self, name: str, start: date, duration: timedelta, margin: timedelta=None):
        super().__init__(name)
        self.start = start
        self.duration = duration
        self.margin = timedelta(0) if margin is None else margin

    @property
    def type(self) -> PlanObjectType:
        return PlanObjectType.TASK
    
    def to_dict(self):
        data = super().to_dict()
        data['start'] = str(self.start)
        data['duration'] = str(self.duration)
        data['margin'] = str(self.margin)
        return data


class Milestone(PlanObject):
    def __init__(self, name: str, target_date: date):
        super().__init__(name)
        self.target_date = target_date
    
    @property
    def type(self) -> PlanObjectType:
        return PlanObjectType.MILESTONE
    
    def to_dict(self):
        data = super().to_dict()
        data['target_date'] = str(self.target_date)
        return data

class Project():
    def __init__(self,name: str,data: List[PlanObject] = None) -> None:
        self.name = name
        self.data = [] if data is None else data

    def to_dict(self):
        return {self.name: [d.to_dict() for d in self.data]}

