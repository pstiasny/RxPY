from six import add_metaclass
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable
from rx.concurrency import immediate_scheduler, current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableCreation(Observable):

    @classmethod
    def defer(cls, observable_factory):
        """Returns an observable sequence that invokes the specified factory 
        function whenever a new observer subscribes.
     
        1 - res = rx.Observable.defer(lambda: rx.Observable.from_array([1,2,3]))    
    
        observable_factory -- Observable factory function to invoke for each 
            observer that subscribes to the resulting sequence.
    
        Returns an observable sequence whose observers trigger an invocation 
        of the given observable factory function.
        """

        def subscribe(observer):
            result = None
            try:
                result = observable_factory()
            except Exception as ex:
                return Observable.throw_exception(ex).subscribe(observer)
            
            return result.subscribe(observer)
        return AnonymousObservable(subscribe)