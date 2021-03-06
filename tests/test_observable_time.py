import logging
from datetime import datetime, timedelta

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

FORMAT = '%(asctime)-15s %(threadName)s %(message)s'
logging.basicConfig(filename='rx.log', format=FORMAT, level=logging.DEBUG)
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger('Rx')

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

def test_window_with_time_or_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        def projection(w, i):
            def inner_proj(x):
                log.info("%s %s" % (i, x))
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"), on_next(420, "3 8"), on_next(470, "4 9"), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_time_or_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))
    
    def create():
        def projection(w, i):
            def inner_proj(x):
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"), on_next(420, "3 8"), on_next(470, "4 9"), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_time_or_count_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        def projection(w, i):
            def inner_proj(x):
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()
    
    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_buffer_with_time_or_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"), on_next(440, "8"), on_next(510, "9"), on_next(580, ""), on_next(600, ""), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_or_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))
    
    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))
        
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"), on_next(440, "8"), on_next(510, "9"), on_next(580, ""), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_or_count_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_oneshot_timer_timespan_basic():
    scheduler = TestScheduler()

    def create():
        return Observable.timer(duetime=300, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(500, 0), on_completed(500))

def test_oneshot_timer_timespan_zero():
    scheduler = TestScheduler()

    def create():
        return Observable.timer(0, scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(201, 0), on_completed(201))

def test_oneshot_timer_timespan_negative():
    scheduler = TestScheduler()

    def create():    
        return Observable.timer(-1, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(201, 0), on_completed(201))

def test_oneshot_timer_timespan_disposed():
    scheduler = TestScheduler()

    def create():
        return Observable.timer(1000, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_oneshot_timer_timespan_observer_throws():
    scheduler1 = TestScheduler()
    xs = Observable.timer(1, scheduler=scheduler1)
    xs.subscribe(lambda x: _raise("ex"))
    
    try:
        return scheduler1.start()
    except RxException:
        pass

    scheduler2 = TestScheduler()
    ys = Observable.timer(1, period=None, scheduler=scheduler2)
    ys.subscribe(on_completed=lambda: _raise("ex"))
    
    try:
        return scheduler2.start()
    except RxException:
        pass

def test_interval_timespan_basic():
    
    scheduler = TestScheduler()
    
    def create():
        return Observable.interval(100, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(300, 0), on_next(400, 1), on_next(500, 2), on_next(600, 3), on_next(700, 4), on_next(800, 5), on_next(900, 6))

def test_interval_timespan_zero():    
    scheduler = TestScheduler()

    def create():
        return Observable.interval(0, scheduler=scheduler)

    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(201, 0), on_next(202, 1), on_next(203, 2), on_next(204, 3), on_next(205, 4), on_next(206, 5), on_next(207, 6), on_next(208, 7), on_next(209, 8))

def test_interval_timespan_negative():    
    scheduler = TestScheduler()
    def create():
        return Observable.interval(-1, scheduler=scheduler)

    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(201, 0), on_next(202, 1), on_next(203, 2), on_next(204, 3), on_next(205, 4), on_next(206, 5), on_next(207, 6), on_next(208, 7), on_next(209, 8))

def test_interval_timespan_disposed():
    scheduler = TestScheduler()

    def create():
        return Observable.interval(1000, scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_interval_timespan_observer_throws():
    scheduler = TestScheduler()
    xs = Observable.interval(1, scheduler=scheduler)
    xs.subscribe(lambda x: _raise("ex"))
    
    try:
        return scheduler.start()
    except RxException:
        pass

def test_throttle_timespan_allpass():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_completed(550))
    
    def create():
        return xs.throttle(40, scheduler)
    
    results = scheduler.start(create)
        
    return results.messages.assert_equal(on_next(290, 3), on_next(340, 4), on_next(390, 5), on_next(440, 6), on_next(490, 7), on_next(540, 8), on_completed(550))

def test_throttle_timespan_allpass_error_end():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_error(550, ex))
    
    def create():
        return xs.throttle(40, scheduler)
    
    results = scheduler.start(create)
    return results.messages.assert_equal(on_next(290, 3), on_next(340, 4), on_next(390, 5), on_next(440, 6), on_next(490, 7), on_next(540, 8), on_error(550, ex))

def test_throttle_timespan_alldrop():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_completed(550))
    
    def create():
        return xs.throttle(60, scheduler)
    
    results = scheduler.start(create)
    return results.messages.assert_equal(on_next(550, 8), on_completed(550))

def test_throttle_timespan_alldrop_error_end():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_error(550, ex))
    
    def create():
        return xs.throttle(60, scheduler)
    
    results = scheduler.start(create)
    return results.messages.assert_equal(on_error(550, ex))

def test_throttle_timespan_some_drop():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(370, 4), on_next(421, 5), on_next(480, 6), on_next(490, 7), on_next(500, 8), on_completed(600))
    
    def create():
        return xs.throttle(50, scheduler)
    
    results = scheduler.start(create)    
    return results.messages.assert_equal(on_next(300, 2), on_next(420, 4), on_next(471, 5), on_next(550, 8), on_completed(600))

def test_throttle_empty():
    scheduler = TestScheduler()
    
    def create():
        return Observable.empty(scheduler).throttle(10, scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_completed(201))

def test_throttle_error():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.throw_exception(ex, scheduler).throttle(10, scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_throttle_never():
    scheduler = TestScheduler()
    
    def create():
        return Observable.never().throttle(10, scheduler)
    
    results = scheduler.start(create)    
    results.messages.assert_equal()

def test_throttle_duration_delay_behavior():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, -1), on_next(250, 0), on_next(280, 1), on_next(310, 2), on_next(350, 3), on_next(400, 4), on_completed(550))
    ys = [scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99))]
    
    def create():
        def selector(x):
            return ys[x]
        
        return xs.throttle_with_selector(selector)

    results = scheduler.start(create)
            
    results.messages.assert_equal(on_next(250 + 20, 0), on_next(280 + 20, 1), on_next(310 + 20, 2), on_next(350 + 20, 3), on_next(400 + 20, 4), on_completed(550))
    xs.subscriptions.assert_equal(subscribe(200, 550))
    ys[0].subscriptions.assert_equal(subscribe(250, 250 + 20))
    ys[1].subscriptions.assert_equal(subscribe(280, 280 + 20))
    ys[2].subscriptions.assert_equal(subscribe(310, 310 + 20))
    ys[3].subscriptions.assert_equal(subscribe(350, 350 + 20))
    ys[4].subscriptions.assert_equal(subscribe(400, 400 + 20))

def test_throttle_duration_throttle_behavior():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, -1), on_next(250, 0), on_next(280, 1), on_next(310, 2), on_next(350, 3), on_next(400, 4), on_completed(550))
    ys = [scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(40, 42), on_next(45, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(60, 42), on_next(65, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99))]


    def create():
        def selector(x):
            return ys[x]
        return xs.throttle_with_selector(selector)
        
    results = scheduler.start(create)

    results.messages.assert_equal(on_next(250 + 20, 0), on_next(310 + 20, 2), on_next(400 + 20, 4), on_completed(550))
    xs.subscriptions.assert_equal(subscribe(200, 550))
    ys[0].subscriptions.assert_equal(subscribe(250, 250 + 20))
    ys[1].subscriptions.assert_equal(subscribe(280, 310))
    ys[2].subscriptions.assert_equal(subscribe(310, 310 + 20))
    ys[3].subscriptions.assert_equal(subscribe(350, 400))
    ys[4].subscriptions.assert_equal(subscribe(400, 400 + 20))

def test_throttle_duration_early_completion():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, -1), on_next(250, 0), on_next(280, 1), on_next(310, 2), on_next(350, 3), on_next(400, 4), on_completed(410))
    ys = [scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(40, 42), on_next(45, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(60, 42), on_next(65, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99))]
    
    def create():
        def selector(x):
            return ys[x]
        return xs.throttle_with_selector(selector)
            
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(250 + 20, 0), on_next(310 + 20, 2), on_next(410, 4), on_completed(410))
    xs.subscriptions.assert_equal(subscribe(200, 410))
    ys[0].subscriptions.assert_equal(subscribe(250, 250 + 20))
    ys[1].subscriptions.assert_equal(subscribe(280, 310))
    ys[2].subscriptions.assert_equal(subscribe(310, 310 + 20))
    ys[3].subscriptions.assert_equal(subscribe(350, 400))
    ys[4].subscriptions.assert_equal(subscribe(400, 410))

def test_throttle_duration_inner_error():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))
    ex = 'ex'
    
    def create():
        def selector(x):
            if x < 4:
                return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
            else:
                return scheduler.create_cold_observable(on_error(x * 10, ex))
            
        return xs.throttle_with_selector(selector)
        
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(450 + 4 * 10, ex))
    xs.subscriptions.assert_equal(subscribe(200, 490))

def test_throttle_duration_outer_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(450, 4), on_error(460, ex))
    
    def create():
        def selector(x):
            return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
        return xs.throttle_with_selector(selector)
        
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(460, ex))
    xs.subscriptions.assert_equal(subscribe(200, 460))

def test_throttle_duration_selector_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))
    
    def create():
        def selector(x):
            if x < 4:
                return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
            else:
                _raise(ex)
            
        return xs.throttle_with_selector(selector)
        
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(450, ex))
    xs.subscriptions.assert_equal(subscribe(200, 450))

def test_throttle_duration_inner_done_delay_behavior():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))
    
    def create():
        def selector(x):
            return scheduler.create_cold_observable(on_completed(x * 10))
        return xs.throttle_with_selector(selector)
            
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_next(450 + 4 * 10, 4), on_completed(550))
    xs.subscriptions.assert_equal(subscribe(200, 550))

def test_throttle_duration_inner_done_throttle_behavior():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(280, 3), on_next(300, 4), on_next(400, 5), on_next(410, 6), on_completed(550))
    
    def create():
        def selector(x):
            return scheduler.create_cold_observable(on_completed(x * 10))
        return xs.throttle_with_selector(selector)

    results = scheduler.start(create)        
    
    results.messages.assert_equal(on_next(250 + 2 * 10, 2), on_next(300 + 4 * 10, 4), on_next(410 + 6 * 10, 6), on_completed(550))
    xs.subscriptions.assert_equal(subscribe(200, 550))

# def test_window_time_basic():
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(240, 3), on_next(270, 4), on_next(320, 5), on_next(360, 6), on_next(390, 7), on_next(410, 8), on_next(460, 9), on_next(470, 10), on_completed(490))
    
#     def create():
#         def selector(ys, i):
#             def proj(y):
#                 return "%s %s" % (i, y)
#             return ys.select(proj).concat(Observable.return_value('%s end' % i))    
#         return xs.window_with_time(100, scheduler=scheduler).select(selector).merge_observable()
    
#     results = scheduler.start(create)
        
#     results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(270, "0 4"), on_next(300, "0 end"), on_next(320, "1 5"), on_next(360, "1 6"), on_next(390, "1 7"), on_next(400, "1 end"), on_next(410, "2 8"), on_next(460, "2 9"), on_next(470, "2 10"), on_next(490, "2 end"), on_completed(490))
#     xs.subscriptions.assert_equal(subscribe(200, 490))

# def test_Window_Time_Basic_Both():
#     , xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(240, 3), on_next(270, 4), on_next(320, 5), on_next(360, 6), on_next(390, 7), on_next(410, 8), on_next(460, 9), on_next(470, 10), on_completed(490))
#     results = scheduler.start(create)
#         return xs.window_with_time(100, 50, scheduler).select(function (ys, i) {
#             return ys.select(function (y) {
#                 return i + " " + y
#             }).concat(Observable.returnValue(i + " end"))
#         }).merge_observable()
    
#     results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(270, "0 4"), on_next(270, "1 4"), on_next(300, "0 end"), on_next(320, "1 5"), on_next(320, "2 5"), on_next(350, "1 end"), on_next(360, "2 6"), on_next(360, "3 6"), on_next(390, "2 7"), on_next(390, "3 7"), on_next(400, "2 end"), on_next(410, "3 8"), on_next(410, "4 8"), on_next(450, "3 end"), on_next(460, "4 9"), on_next(460, "5 9"), on_next(470, "4 10"), on_next(470, "5 10"), on_next(490, "4 end"), on_next(490, "5 end"), on_completed(490))
#     xs.subscriptions.assert_equal(subscribe(200, 490))


class TimeInterval(object):
    def __init__(self, value, interval):
        if isinstance(interval, timedelta):
            interval = int(interval.microseconds/1000.0)

        self.value = value
        self.interval = interval

    def __str__(self):
        return "%s@%s" % (self.value, self.interval)
    
    def equals(other):
        return other.interval == self.interval and other.value == self.value

def test_time_interval_regular():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))
    
    def create():
        def selector(x):
            return TimeInterval(x.value, x.interval)
        return xs.time_interval(scheduler).select(selector).dump()
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, TimeInterval(2, 10)), on_next(230, TimeInterval(3, 20)), on_next(260, TimeInterval(4, 30)), on_next(300, TimeInterval(5, 40)), on_next(350, TimeInterval(6, 50)), on_completed(400))

def test_time_interval_empty():
    scheduler = TestScheduler()
    
    def create():
        return Observable.empty(scheduler).time_interval(scheduler)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_completed(201))

def test_time_interval_error():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.throw_exception(ex, scheduler).time_interval(scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_time_interval_never():
    scheduler = TestScheduler()
    def create():
        return Observable.never().time_interval(scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

class Timestamp(object):
    def __init__(self, value, timestamp):
        if isinstance(timestamp, datetime):
            timestamp = timestamp-datetime.fromtimestamp(0)
            timestamp = int(timestamp.microseconds/1000)

        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return "%s@%s" % (self.value, self.timestamp)
    
    def equals(other):
        return other.timestamp == self.timestamp and other.value == self.value

def test_timestamp_regular():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))
    
    def create():
        def selector(x):
            return Timestamp(x.value, x.timestamp)
        return xs.timestamp(scheduler).select(selector)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, Timestamp(2, 210)), on_next(230, Timestamp(3, 230)), on_next(260, Timestamp(4, 260)), on_next(300, Timestamp(5, 300)), on_next(350, Timestamp(6, 350)), on_completed(400))

def test_timestamp_empty():
    scheduler = TestScheduler()

    def create():
        return Observable.empty(scheduler).time_interval(scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(201))

def test_timestamp_error():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.throw_exception(ex, scheduler).time_interval(scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_timestamp_never():
    scheduler = TestScheduler()
    
    def create():
        return Observable.never().time_interval(scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_sample_regular():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_next(380, 7), on_completed(390))
    
    def create():
        return xs.sample(50, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(250, 3), on_next(300, 5), on_next(350, 6), on_next(400, 7), on_completed(400))

def test_sample_error_in_flight():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(310, 6), on_error(330, ex))
    
    def create():
        return xs.sample(50, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(250, 3), on_next(300, 5), on_error(330, ex))

def test_sample_empty():
    scheduler = TestScheduler()
    
    def create():
        return Observable.empty(scheduler=scheduler).sample(0, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(201))

def test_sample_error():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.throw_exception(ex, scheduler=scheduler).sample(0, scheduler=scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(201, ex))

def test_sample_never():    
    scheduler = TestScheduler()
    
    def create():
        return Observable.never().sample(0, scheduler=scheduler)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_timeout_in_time():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))
    
    def create():
        return xs.timeout(500, None, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

def test_timeout_out_of_time():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))
    
    def create():
        return xs.timeout(205, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

def test_timeout_timeout_occurs_1():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(310, 3), on_next(400, 4), on_completed(500))
    ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(350, -1), on_next(500, -2), on_next(610, -3), on_completed(620))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(300, 620))

def test_timeout_timeout_occurs_2():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(310, 4), on_next(430, 5), on_completed(500))
    ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(240, 3), on_next(310, 4), on_next(460, -1), on_next(610, -2), on_next(720, -3), on_completed(730))
    xs.subscriptions.assert_equal(subscribe(200, 410))
    ys.subscriptions.assert_equal(subscribe(410, 730))

def test_timeout_timeout_occurs_never():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(310, 4), on_next(430, 5), on_completed(500))
    ys = scheduler.create_cold_observable()
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(240, 3), on_next(310, 4))
    xs.subscriptions.assert_equal(subscribe(200, 410))
    ys.subscriptions.assert_equal(subscribe(410, 1000))

def test_timeout_timeout_occurs_completed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_completed(500))
    ys = scheduler.create_cold_observable(on_next(100, -1))

    def create():
        return xs.timeout(100, ys, scheduler=scheduler)

    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(400, -1))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(300, 1000))

def test_timeout_timeout_occurs_error():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_error(500, 'ex'))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(400, -1))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(300, 1000))

def test_timeout_timeout_not_occurs_completed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_completed(250))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))
    ys.subscriptions.assert_equal()

def test_timeout_timeout_not_occurs_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_error(250, ex))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(250, ex))
    xs.subscriptions.assert_equal(subscribe(200, 250))
    ys.subscriptions.assert_equal()

def test_timeout_timeout_does_not_occur():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(320, 4), on_next(410, 5), on_completed(500))
    ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))
    
    def create():
        return xs.timeout(100, ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(240, 3), on_next(320, 4), on_next(410, 5), on_completed(500))
    xs.subscriptions.assert_equal(subscribe(200, 500))
    ys.subscriptions.assert_equal()

def test_timeout_datetime_offset_timeout_occurs():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(410, 1))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(500, -1))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(400, 1000))

def test_timeout_datetime_offset_timeout_does_not_occur_completed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_completed(390))
    ys = scheduler.create_cold_observable(on_next(100, -1))

    def create():
        return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(310, 1), on_completed(390))
    xs.subscriptions.assert_equal(subscribe(200, 390))
    ys.subscriptions.assert_equal()

def test_timeout_datetime_offset_timeout_does_not_occur_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_error(390, ex))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(310, 1), on_error(390, ex))
    xs.subscriptions.assert_equal(subscribe(200, 390))
    ys.subscriptions.assert_equal()

def test_timeout_datetime_offset_timeout_occur_2():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable(on_next(100, -1))
    
    def create():
        return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(500, -1))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(400, 1000))

def test_timeout_datetime_offset_timeout_occur_3():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    
    def create():
        return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(310, 1), on_next(350, 2))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(400, 1000))

def test_timeout_duration_simple_never():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    
    def create():
        def selector(x):
            return ys
        return xs.timeout_with_selector(ys, selector)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    xs.subscriptions.assert_equal(subscribe(200, 450))
    ys.subscriptions.assert_equal(subscribe(200, 310), subscribe(310, 350), subscribe(350, 420), subscribe(420, 450))

def test_timeout_duration_simple_timeout_first():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable(on_next(100, 'boo!'))
    zs = scheduler.create_cold_observable()

    def create():
        return xs.timeout_with_selector(ys, lambda x: zs)

    results = scheduler.start(create)
        
    assert(len(results.messages) == 1)
    assert(results.messages[0].time == 300 and results.messages[0].value.exception)
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(200, 300))
    zs.subscriptions.assert_equal()

def test_timeout_duration_simple_timeout_later():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    zs = scheduler.create_cold_observable(on_next(50, 'boo!'))
    
    def create():
        return xs.timeout_with_selector(ys, lambda _: zs)
    
    results = scheduler.start(create)
        
    assert(len(results.messages) == 3)
    assert(on_next(310, 1).equals(results.messages[0]))
    assert(on_next(350, 2).equals(results.messages[1]))
    assert(results.messages[2].time == 400 and results.messages[2].value.exception)
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(200, 310))
    zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

def test_timeout_duration_simple_timeout_by_completion():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    zs = scheduler.create_cold_observable(on_completed(50))
    
    def create():
        return xs.timeout_with_selector(ys, lambda _: zs)
    
    results = scheduler.start(create)
        
    assert(len(results.messages) == 3)
    assert(on_next(310, 1).equals(results.messages[0]))
    assert(on_next(350, 2).equals(results.messages[1]))
    assert(results.messages[2].time == 400 and results.messages[2].value.exception)
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(200, 310))
    zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

def test_timeout_duration_simple_timeout_by_completion():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    zs = scheduler.create_cold_observable()

    def create():
        def selector(x):
            if x < 3:
                return zs
            else:
                _raise(ex)
            
        return xs.timeout_with_selector(ys, selector)

    results = scheduler.start(create)
            
    results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(420, ex))
    xs.subscriptions.assert_equal(subscribe(200, 420))
    ys.subscriptions.assert_equal(subscribe(200, 310))
    zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420))

def test_timeout_duration_simple_inner_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable()
    zs = scheduler.create_cold_observable(on_error(50, ex))
    
    def create():
        return xs.timeout_with_selector(ys, lambda _: zs)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_error(400, ex))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    ys.subscriptions.assert_equal(subscribe(200, 310))
    zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

def test_timeout_duration_simple_first_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
    ys = scheduler.create_cold_observable(on_error(50, ex))
    zs = scheduler.create_cold_observable()
    
    def create():
        return xs.timeout_with_selector(ys, lambda _: zs)
        
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(250, ex))
    xs.subscriptions.assert_equal(subscribe(200, 250))
    ys.subscriptions.assert_equal(subscribe(200, 250))
    zs.subscriptions.assert_equal()

def test_timeout_duration_simple_source_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex))
    ys = scheduler.create_cold_observable()
    zs = scheduler.create_cold_observable()
    
    def create():
        return xs.timeout_with_selector(ys, lambda _: zs)
        
    results = scheduler.start(create)

    results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex))
    xs.subscriptions.assert_equal(subscribe(200, 450))
    ys.subscriptions.assert_equal(subscribe(200, 310))
    zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420), subscribe(420, 450))

def test_generate_timespan_finite():    
    scheduler = TestScheduler()
    
    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: x <= 3,
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

def test_generate_timespan_throw_condition():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: _raise(ex),
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)
        
    results = scheduler.start(create)    
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_throw_result_selector():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise(ex),
            lambda x: x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create) 
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_throw_iterate():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: _raise(ex),
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

def test_generate_timespan_throw_timeselector():
    ex = 'ex'
    scheduler = TestScheduler()
    
    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: _raise(ex),
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_Dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))

def test_generate_datetime_offset_finite():
    scheduler = TestScheduler()
    
    return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

def test_generate_datetime_offset_throw_condition():
    ex = 'ex'
    scheduler = TestScheduler()
    return Observable.generate_with_relative_time(0, 
            lambda x: _raise(ex),
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_throw_result_selector():
    ex = 'ex'
    scheduler = TestScheduler()
    
    return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise(ex),
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_throw_iterate():
    ex = 'ex'
    scheduler = TestScheduler()
    
    return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: _raise(ex),
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

def test_generate_datetime_offset_throw_time_selector():
    ex = 'ex'
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: _raise(ex),
            scheduler=scheduler)
    
    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_dispose():
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)
    
    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))

def test_window_with_time_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        def selector(w, i):
            return w.select(lambda x: "%s %s" % (i, x))
    
        return xs.window_with_time(100, 70, scheduler=scheduler).select(selector).merge_observable()

    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_time_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))
    
    def create():
        def selector(w, i):
            return w.select(lambda x: "%s %s" % (i, x))
        
        return xs.window_with_time(100, 70, scheduler=scheduler).select(selector).merge_observable()
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_Window_with_time_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        def selector(w, i):
            return w.select(lambda x: "%s %s" % (i, x))
        
        return xs.window_with_time(100, 70, scheduler=scheduler).select(selector).merge_observable()
    
    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_window_with_time_basic_same():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    

    def create():
        def selector(w, i):
            return w.select(lambda x: "%s %s" % (i, x))
        
        return xs.window_with_time(100, scheduler=scheduler).select(selector).merge_observable()
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(380, "1 7"), on_next(420, "2 8"), on_next(470, "2 9"), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        return xs.buffer_with_time(100, 70, scheduler=scheduler).select(lambda x: ",".join([str(a) for a in x]))
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(300, "2,3,4"), on_next(370, "4,5,6"), on_next(440, "6,7,8"), on_next(510, "8,9"), on_next(580, ""), on_next(600, ""), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))
    
    def create():
        return xs.buffer_with_time(100, 70, scheduler=scheduler).select(lambda x: ",".join([str(a) for a in x]))
    
    results = scheduler.start(create)    
    
    results.messages.assert_equal(on_next(300, "2,3,4"), on_next(370, "4,5,6"), on_next(440, "6,7,8"), on_next(510, "8,9"), on_next(580, ""), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        return xs.buffer_with_time(100, 70, scheduler=scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(300, "2,3,4"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_buffer_with_time_basic_same():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        return xs.buffer_with_time(100, scheduler=scheduler).select(lambda x: ",".join([str(a) for a in x]))
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(300, "2,3,4"), on_next(400, "5,6,7"), on_next(500, "8,9"), on_next(600, ""), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

# Delay with selector
def test_delay_duration_simple1():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 10), on_next(220, 30), on_next(230, 50), on_next(240, 35), on_next(250, 20), on_completed(260))
    
    def create():
        def selector(x):
            return scheduler.create_cold_observable(on_next(x, '!'))
    
        return xs.delay_with_selector(selector)
            
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(210 + 10, 10), on_next(220 + 30, 30), on_next(250 + 20, 20), on_next(240 + 35, 35), on_next(230 + 50, 50), on_completed(280))
    xs.subscriptions.assert_equal(subscribe(200, 260))

def test_delay_duration_simple2():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_next(250, 6), on_completed(300))
    ys = scheduler.create_cold_observable(on_next(10, '!'))
    
    def create():
        return xs.delay_with_selector(lambda _: ys)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210 + 10, 2), on_next(220 + 10, 3), on_next(230 + 10, 4), on_next(240 + 10, 5), on_next(250 + 10, 6), on_completed(300))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(210, 220), subscribe(220, 230), subscribe(230, 240), subscribe(240, 250), subscribe(250, 260))

def test_delay_duration_simple3():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_next(250, 6), on_completed(300))
    ys = scheduler.create_cold_observable(on_next(100, '!'))
    
    def create():
        return xs.delay_with_selector(lambda _: ys)
    
    results = scheduler.start(create)    
    
    results.messages.assert_equal(on_next(210 + 100, 2), on_next(220 + 100, 3), on_next(230 + 100, 4), on_next(240 + 100, 5), on_next(250 + 100, 6), on_completed(350))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(210, 310), subscribe(220, 320), subscribe(230, 330), subscribe(240, 340), subscribe(250, 350))

def test_delay_duration_simple4_inner_empty():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_next(250, 6), on_completed(300))
    ys = scheduler.create_cold_observable(on_completed(100))
    
    def create():
        return xs.delay_with_selector(lambda _: ys)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(210 + 100, 2), on_next(220 + 100, 3), on_next(230 + 100, 4), on_next(240 + 100, 5), on_next(250 + 100, 6), on_completed(350))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(210, 310), subscribe(220, 320), subscribe(230, 330), subscribe(240, 340), subscribe(250, 350))

def test_delay_duration_dispose1():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_next(250, 6), on_completed(300))
    ys = scheduler.create_cold_observable(on_next(200, '!'))
    
    def create():
        return xs.delay_with_selector(lambda _: ys)
        
    results = scheduler.start(create, disposed=425)
    results.messages.assert_equal(on_next(210 + 200, 2), on_next(220 + 200, 3))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(210, 410), subscribe(220, 420), subscribe(230, 425), subscribe(240, 425), subscribe(250, 425))

def test_delay_duration_dispose2():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(400, 3), on_completed(500))
    ys = scheduler.create_cold_observable(on_next(50, '!'))
    
    def create():
        return xs.delay_with_selector(lambda _: ys)
        
    results = scheduler.start(create, disposed=300)
    results.messages.assert_equal(on_next(210 + 50, 2))
    xs.subscriptions.assert_equal(subscribe(200, 300))
    ys.subscriptions.assert_equal(subscribe(210, 260))


# // TakeLastBuffer
# def test_takeLastBuffer_with_time_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)
    
#     res.messages.assert_equal(on_next(230, function (lst) {
#         return lst.length === 0
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)
    
#     res.messages.assert_equal(on_next(230, function (lst) {
#         return lst.length === 0
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# function arrayEqual(arr1, arr2) {
#     if (arr1.length != arr2.length) return false
#     for (var i = 0, len = arr1.length i < len i++) {
#         if (arr1[i] != arr2[i]) return false
#     }
#     return true
# }

# def test_takeLastBuffer_with_time_Some1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)
    
#     res.messages.assert_equal(on_next(240, function (lst) {
#         return arrayEqual(lst, [2, 3])
#     }), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))

# def test_takeLastBuffer_with_time_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)
    
#     res.messages.assert_equal(on_next(300, function (lst) {
#         return lst.length === 0
#     }), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some3():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(45, scheduler)
    
#     res.messages.assert_equal(on_next(300, function (lst) {
#         return arrayEqual(lst, [6, 7, 8, 9])
#     }), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some4():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)
    
#     res.messages.assert_equal(on_next(350, function (lst) {
#         return lst.length === 0
#     }), on_completed(350))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_takeLastBuffer_with_time_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)
    
#     res.messages.assert_equal(on_next(230, function (lst) {
#         return arrayEqual(lst, [1, 2])
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_takeLastBuffer_with_time_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_Take_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_completed(201))
#     xs.subscriptions.assert_equal(subscribe(200, 201))

# def test_Take_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeWithTime(25, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(225))
#     xs.subscriptions.assert_equal(subscribe(200, 225))

# def test_Take_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Take_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_Take_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_Take_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(55, scheduler).takeWithTime(35, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))

# def test_Take_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(35, scheduler).takeWithTime(55, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))


# // Skip
# def test_Skip_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Skip_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipWithTime(15, scheduler)
    
#     res.messages.assert_equal(on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Skip_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Skip_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.skipWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_Skip_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.skipWithTime(50, scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_Skip_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipWithTime(15, scheduler).skipWithTime(30, scheduler)
    
#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))

# def test_Skip_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipWithTime(30, scheduler).skipWithTime(15, scheduler)
    
#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))


# // TakeLast
# def test_TakeLast_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero1_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler, scheduler)
    
#     res.messages.assert_equal(on_completed(231))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero2_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler, scheduler)
    
#     res.messages.assert_equal(on_completed(231))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Some1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)
    
#     res.messages.assert_equal(on_next(240, 2), on_next(240, 3), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_TakeLast_Some1_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)
    
#     res.messages.assert_equal(on_next(241, 2), on_next(242, 3), on_completed(243))
#     xs.subscriptions.assert_equal(subscribe(200, 240))

# def test_TakeLast_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)
    
#     res.messages.assert_equal(on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))


# def test_TakeLast_Some2_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)
    
#     res.messages.assert_equal(on_completed(301))
#     xs.subscriptions.assert_equal(subscribe(200, 300))


# def test_TakeLast_Some3():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(45, scheduler)
    
#     res.messages.assert_equal(on_next(300, 6), on_next(300, 7), on_next(300, 8), on_next(300, 9), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_TakeLast_Some3_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(45, scheduler, scheduler)
    
#     res.messages.assert_equal(on_next(301, 6), on_next(302, 7), on_next(303, 8), on_next(304, 9), on_completed(305))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_TakeLast_Some4():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)
    
#     res.messages.assert_equal(on_completed(350))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_TakeLast_Some4_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)
    
#     res.messages.assert_equal(on_completed(351))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_TakeLast_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_next(230, 1), on_next(230, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# def test_TakeLast_All_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)
    
#     res.messages.assert_equal(on_next(231, 1), on_next(232, 2), on_completed(233))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_TakeLast_Error_WithLoopScheduler():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_TakeLast_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLast_Never_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# // Skiplast
# def test_SkipLast_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipLast_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(0, scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipLast_Some1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(15, scheduler)
    
#     res.messages.assert_equal(on_next(230, 1), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipLast_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(45, scheduler)
    
#     res.messages.assert_equal(on_next(260, 1), on_next(270, 2), on_next(280, 3), on_next(290, 4), on_next(300, 5), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_SkipLast_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(45, scheduler)
    
#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipLast_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(45, scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_SkipLast_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.skipLastWithTime(50, scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# // SkipUntil
# def test_SkipUntil_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(0), scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipUntil_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipUntil_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_SkipUntil_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_SkipUntil_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(215), scheduler).skipUntilWithTime(Date(230), scheduler)
    
#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))

# def test_SkipUntil_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(230), scheduler).skipUntilWithTime(Date(215), scheduler)
    
#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))


# // TakeUntil
# def test_TakeUntil_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(0), scheduler)
    
#     res.messages.assert_equal(on_completed(201))
#     xs.subscriptions.assert_equal(subscribe(200, 201))

# def test_TakeUntil_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeUntil_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_TakeUntil_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(250), scheduler)
    
#     res.messages.assert_equal(on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_TakeUntil_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(255), scheduler).takeUntilWithTime(Date(235), scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))

# def test_TakeUntil_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeUntilWithTime(Date(235), scheduler).takeUntilWithTime(Date(255), scheduler)
    
#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))

if __name__ == '__main__':
    #test_delay_timespan_simple1()
    #test_delay_datetime_offset_simple1_impl()
    #test_window_time_basic()
    
    #test_timeout_timeout_not_occurs_error()
    test_buffer_with_time_or_count_basic()
