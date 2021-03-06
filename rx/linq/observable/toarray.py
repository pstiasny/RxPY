from six import add_metaclass

from rx.observable import Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableToArray(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def to_array(self):
        def accumulator(res, i):
            res.append(i)
            return res[:]
        
        return self.scan(accumulator, seed=[]).start_with([]).final_value()