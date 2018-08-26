import re


def test_uptime(poolcounter, clients):
    """UPTIME fetches uptime"""
    client = clients.get(1)
    client.send('STATS UPTIME')
    recv = client.receive()
    assert re.search('uptime: \d+ days, \d+h \d+m \d+s', recv)


def test_full(poolcounter, clients):
    """FULL fetches lots of stuff"""
    client = clients.get(1)
    client.send('STATS FULL')
    recv = client.receive()
    assert re.search('uptime: \d+ days, \d+h \d+m \d+s', recv)
    assert re.search(
        'total processing time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        'average processing time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        'gained time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        'waiting time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        'waiting time for me: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        'waiting time for anyone: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        'waiting time for good: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        'wasted timeout time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search('total_acquired: \d+', recv)
    assert re.search('total_releases: \d+', recv)
    assert re.search('hashtable_entries: \d+', recv)
    assert re.search('processing_workers: \d+', recv)
    assert re.search('waiting_workers: \d+', recv)
    assert re.search('connect_errors: \d+', recv)
    assert re.search('failed_sends: \d+', recv)
    assert re.search('full_queues: \d+', recv)
    assert re.search('lock_mismatch: \d+', recv)
    assert re.search('lock_while_waiting: \d+', recv)
    assert re.search('release_mismatch: \d+', recv)
    assert re.search('processed_count: \d+', recv)


def test_waiting_workers(poolcounter, clients):
    """waiting_workers is 0 because we aren't running concurrent tests"""
    client = clients.get(1)
    client.send('STATS waiting_workers')
    assert client.receive() == 'waiting_workers: 0'


def test_hashtable_entries(poolcounter, clients):
    """hashtable_entries is 0 because we aren't running concurrent tests"""
    client = clients.get(1)
    client.send('STATS hashtable_entries')
    assert client.receive() == 'hashtable_entries: 0'
