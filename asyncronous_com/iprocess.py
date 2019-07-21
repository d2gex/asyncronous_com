import abc


class IProcess(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def clean(self):
        pass

    @abc.abstractmethod
    def run(self, loops=True):
        pass