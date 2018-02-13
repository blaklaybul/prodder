import pytest
from prodder import ProdderEvents, Prodder, EmptyTaskList, gen_fake_header


@pytest.fixture
def test_event():
    return 1


@pytest.fixture
def empty_prodder():
    """Returns a default prodder instance with empty task list"""
    return Prodder([])


@pytest.fixture
def prodder():
    tasks = ['http://blak.la/{}'.format(i) for i in range(100)]
    prodder = Prodder(tasks)
    return prodder

@pytest.fixture
def default_prodder_events():
    """Returns a prodder event system with no registered events"""
    return ProdderEvents()


@pytest.fixture
def prodder_events():
    prodder_events = ProdderEvents()
    prodder_events.on("test", test_event)
    return prodder_events


def test_default_params(empty_prodder):
    assert empty_prodder.tasks == []
    assert empty_prodder.lifespan == 60
    assert empty_prodder.high == 100
    assert empty_prodder.rpm == (60 / 100)


def test_set_tasks(prodder):
    tasks = ['http://blak.la/{}'.format(i) for i in range(100)]
    assert prodder.tasks == tasks


def test_set_headers():
    header = gen_fake_header()
    prodder = Prodder([], header=header)
    assert prodder.header == header


def test_set_lifespan():
    lifespan = 60
    prodder = Prodder([], lifespan=lifespan)
    assert prodder.dd == (prodder.start + lifespan)


def test_prod_on_empty_prodder(empty_prodder):
    with pytest.raises(EmptyTaskList):
        empty_prodder.prod()


def test_prodder_events(default_prodder_events):
    assert default_prodder_events.eventListeners == {}


def test_add_event(prodder_events):
    assert prodder_events.eventListeners == {"test": [test_event]}


def test_trigger_event(prodder_events):
    assert prodder_events.trigger("test") == 1