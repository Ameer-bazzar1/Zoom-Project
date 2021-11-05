from abc import ABC, abstractmethod


class Student:
    _id = 0
    _name = ""
    _attendance = []
    _participate_counter = 0
    _participate = []

    def __init__(self, idNum, name):
        self._id = idNum
        self._name = name
        self._attendance = []
        self._participate = []

    def get_name(self):
        return self._name

    def get_id(self):
        return self._id

    def add_attend(self, parameter='x'):
        self._attendance.append(parameter)

    def add_participate(self):
        self._participate_counter += 1

    def set_final_participate(self):
        self._participate.append(self._participate_counter)
        self._participate_counter = 0

    def toArray(self):
        toArr = [self._id, self._name]
        for i in range(len(self._attendance)):
            toArr.append(self._attendance[i])
        return toArr

    def toArray2(self):
        toArr2 = [self._id, self._name]
        for i in range(len(self._participate)):
            toArr2.append(self._participate[i])
        return toArr2


class Course(ABC):
    _courseName = ""
    _studentsList = []

    def __init__(self, name):
        self._courseName = name

    @abstractmethod
    def add_student(self, parameter=Student(0, '')):
        pass

    @abstractmethod
    def get_courseName(self):
        pass

    @abstractmethod
    def get_studentsList(self):
        pass


class ItCourse(Course):

    def __init__(self, name):
        Course.__init__(self, name)

    def add_student(self, parameter=Student(0, '')):
        self._studentsList.append(parameter)

    def get_courseName(self):
        return self._courseName

    def get_studentsList(self):
        return self._studentsList

    def get_student(self, a=0):
        return self._studentsList[a]


class ENCS3130(ItCourse):
    def __init__(self):
        ItCourse.__init__(self, "ENCS3130")
