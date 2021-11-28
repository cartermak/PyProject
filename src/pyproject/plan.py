import json
from typing import Dict, List, Tuple, Union
from uuid import uuid4
from abc import ABC, abstractmethod
from enum import Enum, auto
import datetime as dt


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
    def __init__(self, name: str, start: dt.date, duration: dt.timedelta, margin: dt.timedelta = None, critical: bool = False):
        super().__init__(name)
        self.start = start
        self.duration = duration
        self.margin = dt.timedelta(0) if margin is None else margin
        self.critical = critical
    
    @property
    def end(self):
        return self.start + self.duration

    @property
    def type(self) -> PlanObjectType:
        return PlanObjectType.TASK

    def to_dict(self):
        data = super().to_dict()
        data['start'] = str(self.start)
        data['duration'] = str(self.duration)
        data['margin'] = str(self.margin)
        data['critical'] = str(self.critical)
        return data


class Milestone(PlanObject):
    def __init__(self, name: str, start: dt.date):
        super().__init__(name)
        self.start = start

    @property
    def type(self) -> PlanObjectType:
        return PlanObjectType.MILESTONE
    
    @property
    def end(self):
        return self.start

    def to_dict(self):
        data = super().to_dict()
        data['start'] = str(self.start)
        return data


class Category(PlanObject):
    def __init__(self, name, start: dt.date = None, duration: dt.timedelta = None, children: List[PlanObject] = None) -> None:
        super().__init__(name)
        self.__start = start
        self.__duration = duration
        self.children = [] if children is None else children

    def add_child(self, child: PlanObject) -> None:
        self.children.append(child)

    @property
    def type(self):
        return PlanObjectType.CATEGORY

    @property
    def start(self):
        s,_ = self.get_time_bounds()
        return s
    
    @property
    def end(self):
        _,e = self.get_time_bounds()
        return e

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['children'] = [c.to_dict() for c in self.children]
        return data
    
    def get_list(self) -> List[PlanObject]:
        data = []
        for c in self.children:
            data.append(c)
            if isinstance(c,Category):
                data.extend(c.get_list())
        
        return data

    # def get_dims(self) -> Tuple[int,int]:
    #     w = 0
    #     hs = []
    #     for c in self.children:
    #         if isinstance(c, (Task,Milestone)):
    #             w += 1
    #             hs.append(1)
    #         elif isinstance(c, Category):
    #             c_w,c_h = c.get_dims()
    #             w += c_w
    #             hs.append(c_h)
    #         else:
    #             raise RuntimeError("Unknown child data type")
        
    #     if hs:
    #         height = max(hs)+1
    #     else:
    #         height = 1
        
    #     return (w,height)
    
    def get_time_bounds(self) -> Tuple[dt.date,dt.date]:
        """Get start and end boundaries based on all children

        Returns:
            Tuple[date,date]: [start_date,end_date]
        """

        if self.__start is not None and self.__duration is not None:
            return (self.__start,self.__start + self.__duration)

        ss = []
        es = []

        for c in self.children:
            if isinstance(c, Task):
                ss.append(c.start)
                es.append((c.start + c.duration))
            elif isinstance(c,Milestone):
                ss.append(c.start)
                es.append(c.start)
            elif isinstance(c, Category):
                c_ss,c_es = c.get_time_bounds()
                ss.append(c_ss)
                es.append(c_es)
            else:
                raise RuntimeError("Unknown child data type")
        
        s = min(ss)
        e = max(es)
        return (s,e)
        


class Project():
    def __init__(self, name: str, data: List[PlanObject] = None) -> None:
        self.name = name
        self.root = Category('root',children=data)
        self.root.id = 0

    def to_dict(self):
        return {self.name: self.root.to_dict()}

    def from_dict(self):
        raise NotImplementedError()

    def get_dims(self) -> int:
        return self.root.get_dims()

    @classmethod
    def from_csv(cls, csv_data, project_name):
        # Necessary ProjectLibre Columns: ID, Name, Start, Duration, Free Slack, Parent ID, Is WBS Parent, Display task as milestone, Critical, Predecessors

        data_list = []
        data_dict = {}

        for line in csv_data:
            id = int(line[0])
            name = line[1]
            start = dt.datetime.strptime(line[2], '%x %I:%M %p').date()
            duration = dt.timedelta(float(line[3].rstrip('?').rstrip('days')))
            margin = line[4]
            parent_id = int(line[5])
            is_parent = line[6] == 'true'
            is_milestone = line[7] == 'true'
            is_critical = line[8] == 'true'
            predecessors = list(map(int,line[9].split(";"))) if line[9] else []

            if is_parent:
                entry = Category(name,start,duration)
            elif is_milestone:
                entry = Milestone(name, start)
            else:
                entry = Task(name, start, duration, margin, is_critical)

            entry.predecessors = predecessors
            entry.id = id
            data_dict[id] = entry

            if parent_id == 0:
                data_list.append(entry)
            else:
                data_dict[parent_id].add_child(entry)
        

        return cls(project_name, data_list)
