from six import add_metaclass
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.concurrency import immediate_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableReturnValue(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def return_value(cls, value, scheduler=None):
        """Returns an observable sequence that contains a single element, 
        using the specified scheduler to send out observer messages.
        There is an alias called 'returnValue' for browsers <IE9.
     
        example
        res = rx.Observable.return(42)
        res = rx.Observable.return(42, rx.Scheduler.timeout)
     
        Keyword arguments:
        value -- Single element in the resulting observable sequence.
        scheduler -- [Optional] Scheduler to send the single element on. If 
            not specified, defaults to Scheduler.immediate.
        
        Returns an observable sequence containing the single specified 
        element."""
        scheduler = scheduler or immediate_scheduler

        def subscribe(observer):
            def action(scheduler, state=None):
                observer.on_next(value)
                observer.on_completed()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

#ObservableReturnValue.setattr("return", ObservableReturnValue.return_value)

