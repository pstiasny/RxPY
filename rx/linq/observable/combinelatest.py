from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableCombineLatest(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def __init__(self, subscribe):
        self.combine_latest = self.__combine_latest

    def __combine_latest(self, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever any of the observable
        sequences produces an element. This can be in the form of an argument 
        list of observables or an array.
     
        1 - obs = observable.combine_latest(obs1, obs2, obs3, function (o1, o2, o3) { return o1 + o2 + o3; })
        2 - obs = observable.combine_latest([obs1, obs2, obs3], function (o1, o2, o3) { return o1 + o2 + o3; })
     
        Returns an observable sequence containing the result of combining 
        elements of the sources using the specified result selector function.
        """
        
        args = list(args)
        if args and isinstance(args[0], list):
            args = args[0]

        args.insert(0, self)
        
        return Observable.combine_latest(*args)
    
    @classmethod
    def combine_latest(cls, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever any of the observable 
        sequences produces an element.
     
        1 - obs = Observable.combine_latest(obs1, obs2, obs3, function (o1, o2, o3) { return o1 + o2 + o3; })
        2 - obs = Observable.combine_latest([obs1, obs2, obs3], function (o1, o2, o3) { return o1 + o2 + o3; })     
     
        Returns an observable sequence containing the result of combining 
        elements of the sources using the specified result selector function.
        """
    
        if args and isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        
        result_selector = args.pop()
         
        def subscribe(observer):
            n = len(args)
            has_value = [False] * n
            has_value_all = [False]
            is_done = [False] * n
            values = [None] * n

            def next(i):
                has_value[i] = True
                
                if has_value_all[0] or all(has_value):
                    try:
                        res = result_selector(*values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    
                    observer.on_next(res)
                elif all([x for j, x in enumerate(is_done) if j != i]):
                    observer.on_completed()

                has_value_all[0] = all(has_value)

            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()
             
            subscriptions = [None] * n
            def func(i):
                subscriptions[i] = SingleAssignmentDisposable()
                
                def on_next(x):
                    values[i] = x
                    next(i)
                
                def on_completed():
                    done(i)
                
                subscriptions[i].disposable = args[i].subscribe(on_next, observer.on_error, on_completed)

            for idx in range(n):
                func(idx)
            return CompositeDisposable(subscriptions)
        return AnonymousObservable(subscribe)
