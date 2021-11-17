import json
from typing import Dict, List, Union
from uuid import uuid4
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import date, timedelta, datetime


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


class Task(PlanObject):
    def __init__(self, name: str, start: date, duration: timedelta, margin: timedelta = None):
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
    def __init__(self, name: str, start: date):
        super().__init__(name)
        self.start = start

    @property
    def type(self) -> PlanObjectType:
        return PlanObjectType.MILESTONE

    def to_dict(self):
        data = super().to_dict()
        data['start'] = str(self.start)
        return data
    


class Category(PlanObject):
    def __init__(self, name, children: List[PlanObject] = None) -> None:
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


class Project():
    def __init__(self, name: str, data: List[PlanObject] = None) -> None:
        self.name = name
        self.data = data

    def to_dict(self):
        return {self.name: [d.to_dict() for d in self.data]}

    def from_dict(self):
        raise NotImplementedError()
    
    
    @classmethod
    def from_csv(cls,csv_data,project_name):
        # Necessary ProjectLibre Columns: Name, Start, Duration, WBS Parent, Total Slack, Is WBS Parent, Display task as milestone

        data_list = []
        data_dict = {}
        

        for line in csv_data:
            id = line[0]
            name = line[1]
            start = datetime.strptime(line[2],'%x %I:%M %p')
            duration = timedelta(float(line[3].rstrip('?').rstrip('days')))
            margin = line[4]
            parent_id = line[5]
            is_parent = line[6] == 'true'
            is_milestone = line[7] == 'true'

            if is_parent:
                entry = Category(name)
            elif is_milestone:
                entry = Milestone(name,start)
            else:
                entry = Task(name,start,duration,margin)
            
            entry.id = id
            data_dict[id] = entry

            if parent_id == '0':
                data_list.append(entry)
            else:
                data_dict[parent_id].add_child(entry)
        
        return cls(project_name,data_list)
