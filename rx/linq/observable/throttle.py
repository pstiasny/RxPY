import logging
from datetime import timedelta
from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

log = logging.getLogger("Rx")

@add_metaclass(ExtensionMethod)
class ObservableThrottle(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def throttle(self, duetime, scheduler):
        scheduler = scheduler or timeout_scheduler
        source = self

        def subscribe(observer):
            cancelable = SerialDisposable()
            has_value = [False]
            value = [None]
            _id = [0]
            
            def on_next(x):
                has_value[0] = True
                value[0] = x
                _id[0] += 1
                current_id = _id[0]
                d = SingleAssignmentDisposable()
                cancelable.disposable = d

                def action(scheduler, state=None):
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])
                    has_value[0] = False
                
                d.disposable = scheduler.schedule_relative(duetime, action)

            def on_error(exception):
                cancelable.dispose()
                observer.on_error(exception)
                has_value[0] = False
                _id[0] += 1

            def on_completed():
                cancelable.dispose()
                if has_value[0]:
                    observer.on_next(value[0])
                
                observer.on_completed()
                has_value[0] = False
                _id[0] += 1
            
            subscription = source.subscribe(on_next, on_error, on_completed) 
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)

    def throttle_with_selector(self, throttle_duration_selector):
        """Ignores values from an observable sequence which are followed by 
        another value within a computed throttle duration.
     
        1 - res = source.delay_with_selector(lambda x: rx.Scheduler.timer(x+x)) 
     
        Keyword arguments:
        throttle_duration_selector -- Selector function to retrieve a sequence 
            indicating the throttle duration for each given element.
        
        Returns the throttled sequence.
        """
        source = self

        def subscribe(observer):
            cancelable = SerialDisposable()
            has_value = [False]
            value = [None]
            _id = [0]

            def on_next(x):
                throttle = None
                try:
                    throttle = throttle_duration_selector(x)
                except Exception as e:
                    observer.on_error(e)
                    return
                
                has_value[0] = True
                value[0] = x
                _id[0] += 1
                current_id = _id[0]
                d = SingleAssignmentDisposable()
                cancelable.disposable = d

                def on_next(x):
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])
                    
                    has_value[0] = False
                    d.dispose()
                
                def on_completed():
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])
                    
                    has_value[0] = False
                    d.dispose()
                
                d.disposable = throttle.subscribe(on_next, observer.on_error, on_completed)
            
            def on_error(e):
                cancelable.dispose()
                observer.on_error(e)
                has_value[0] = False
                _id[0] += 1
            
            def on_completed():
                cancelable.dispose()
                if has_value[0]:
                    observer.on_next(value[0])
                
                observer.on_completed()
                has_value[0] = False
                _id[0] += 1

            subscription = source.subscribe(on_next, on_error, on_completed)
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)
