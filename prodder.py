import itertools
from datetime import datetime, timedelta
import time
import requests
import requests.exceptions as reqex
from faker import Faker


def gen_fake_header():
    fake = Faker()
    header = {}
    header['X-Forwarded-User'] = fake.user_name()
    header['user_agent'] = fake.user_agent()
    header['X-Forwarded-For'] = fake.ipv4()
    return header


def print_fmt(*args):
    fmt = "{}|{}|{}|{}|{}|{}"
    if args:
        print(fmt.format(*args))

class EmptyTaskList(Exception):
    pass


class ProdderEvents(object):
    def __init__(self):
        self.listeners = {}

    def on(self, event, f):
        if event in self.listeners:
            self.listeners[event].append(f)
        else:
            self.listeners[event] = [f]

    def trigger(self, event):
        if event in self.listeners:
            for func in self.listeners[event]:
                return func()


class Prodder(ProdderEvents):
    def __init__(self, tasks, lifespan=60, high=100, header=gen_fake_header()):
        super().__init__()
        self.tasks = tasks
        self.start = datetime.now()
        self.lifespan = lifespan
        self.end = self.start + timedelta(seconds=self.lifespan)
        self.high = high
        self.rpm = 60/self.high
        self.header = header

    def prod(self):
        if not self.tasks:
            raise EmptyTaskList("""prodder task list is empty - no sites to crawl.
                Please initialize prodder with urls.""")

        while datetime.now() < self.end:
            for task in self.tasks:
                time.sleep(self.rpm)
                try:
                    r = requests.get(task, headers=self.header)
                    print_fmt(
                        datetime.now(),
                        r.status_code,
                        r.request.url,
                        self.header['X-Forwarded-User'],
                        self.header["user_agent"],
                        self.header["X-Forwarded-For"])
                    self.trigger('prod')
                except reqex.RequestException as ce:
                    # just handle baseclass exceptions for now
                    print(ce)
                    self.trigger('err')

if __name__ == "__main__":
    tasks = ['http://blak.la/ybul']
    mike = Prodder(tasks)
    mike.prod()