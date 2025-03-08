from abc import ABC, abstractmethod

class Optimizer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

    @abstractmethod
    def show_result(self):
        pass