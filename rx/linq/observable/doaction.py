import six

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

@six.add_metaclass(ObservableMeta)
class ObservableDoAction(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def do_action(self, observer=None, on_next=None, on_error=None, on_completed=None):
        """Invokes an action for each element in the observable sequence and 
        invokes an action upon graceful or exceptional termination of the 
        observable sequence. This method can be used for debugging, logging, 
        etc. of query behavior by intercepting the message stream to run 
        arbitrary actions for messages on the pipeline.
    
        1 - observable.do_action(observer)
        2 - observable.do_action(on_next)
        3 - observable.do_action(on_next, on_error)
        4 - observable.do_action(on_next, on_error, on_eompleted)
     
        observer -- [Optional] Observer, or ... 
        on_next -- [Optional] Action to invoke for each element in the 
            observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination 
            of the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination 
            of the observable sequence. 
     
        Returns the source sequence with the side-effecting behavior applied.   
        """
        source = self
        if not observer is None:
            on_next = observer.on_next
            on_error = observer.on_error
            on_completed = observer.on_completed
        
        def subscribe(observer):
            def on_next(x):
                try:
                    on_next(x)
                except Exception as e:
                    observer.on_error(e)
                
                observer.on_next(x)

            def on_error(exception):
                if not on_error:
                    observer.on_error(exception)
                else:
                    try:
                        on_error(exception)
                    except Exception as e:
                        observer.on_error(e)
                    
                    observer.on_error(exception)

            def on_completed():
                if not on_completed:
                    observer.on_completed()
                else:
                    try:
                        on_completed()
                    except Exception as e:
                        observer.on_error(e)
                    
                    observer.on_completed()
            return source.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)
