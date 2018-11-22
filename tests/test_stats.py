import re


def test_uptime(poolcounter, clients):
    """UPTIME fetches uptime"""
    client = clients.get(1)
    client.send('STATS UPTIME')
    recv = client.receive()
    assert re.search(r'uptime: \d+ days, \d+h \d+m \d+s', recv)


def test_full(poolcounter, clients):
    """FULL fetches lots of stuff"""
    client = clients.get(1)
    client.send('STATS FULL')
    recv = client.receive()
    assert re.search(r'uptime: \d+ days, \d+h \d+m \d+s', recv)
    assert re.search(
        r'total processing time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        r'average processing time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        r'gained time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        r'waiting time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        r'waiting time for me: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(
        r'waiting time for anyone: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        r'waiting time for good: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s',
        recv)
    assert re.search(
        r'wasted timeout time: (((\d+ days )?\d+h )?\d+m )?\d+(\.\d+)?s', recv)
    assert re.search(r'total_acquired: \d+', recv)
    assert re.search(r'total_releases: \d+', recv)
    assert re.search(r'hashtable_entries: \d+', recv)
    assert re.search(r'processing_workers: \d+', recv)
    assert re.search(r'waiting_workers: \d+', recv)
    assert re.search(r'connect_errors: \d+', recv)
    assert re.search(r'failed_sends: \d+', recv)
    assert re.search(r'full_queues: \d+', recv)
    assert re.search(r'lock_mismatch: \d+', recv)
    assert re.search(r'lock_while_waiting: \d+', recv)
    assert re.search(r'release_mismatch: \d+', recv)
    assert re.search(r'processed_count: \d+', recv)


def test_waiting_workers(poolcounter, clients):
    """Waiting_workers is 0 because we aren't running concurrent tests"""
    client = clients.get(1)
    client.send('STATS waiting_workers')
    assert client.receive() == 'waiting_workers: 0'


def test_hashtable_entries(poolcounter, clients):
    """Hashtable_entries is 0 because we aren't running concurrent tests"""
    client = clients.get(1)
    client.send('STATS hashtable_entries')
    assert client.receive() == 'hashtable_entries: 0'
