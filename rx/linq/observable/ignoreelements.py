from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal import noop
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableIgnoreElements(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    def ignore_elements(self):
        """Ignores all elements in an observable sequence leaving only the 
        termination messages.
     
        Returns an empty observable {Observable} sequence that signals 
        termination, successful or exceptional, of the source sequence."""
        
        source = self

        def subscribe(observer):
            return source.subscribe(noop, observer.on_error, observer.on_completed)
        
        return AnonymousObservable(subscribe)
