import pytest


def test_can_lock(poolcounter, clients, lock_type):
    """Can lock"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'


def test_can_lock_and_release(poolcounter, clients, lock_type):
    """Can lock and release"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('RELEASE')
    assert client.receive() == 'RELEASED'


def test_can_lock_and_release_and_relock(poolcounter, clients, lock_type):
    """Can lock and release and relock"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('RELEASE')
    assert client.receive() == 'RELEASED'
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'


def test_can_lock_and_release_and_relock_and_unlock(
        poolcounter, clients, lock_type):
    """Can lock and release and relock and unlock"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('RELEASE')
    assert client.receive() == 'RELEASED'
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('RELEASE')
    assert client.receive() == 'RELEASED'


def test_release_without_lock(poolcounter, clients):
    """RELEASEing without holding any locks warns"""
    client = clients.get(1)
    client.send('RELEASE')
    assert client.receive() == 'NOT_LOCKED'


def test_locking_holding_four_locks(poolcounter, clients, lock_type):
    """Locking while holding four locks warns"""
    client = clients.get(1)
    for i in range(0, 4):
        client.send('%s l%s 1 1 1' % (lock_type, str(i).encode()))
        assert client.receive() == 'LOCKED'
    client.send('%s l5 1 1 1' % lock_type)
    assert client.receive() == 'LOCK_HELD'


def test_locking_no_timeout(poolcounter, clients, lock_type):
    """Locking with no timeout LOCKs"""
    client = clients.get(1)
    client.send('%s l 1 1 0' % lock_type)
    assert client.receive() == 'LOCKED'


def test_locking_timeout_left_off(poolcounter, clients, lock_type):
    """Locking with timeout left off LOCKs"""
    client = clients.get(1)
    client.send('%s l 1 1' % lock_type)
    assert client.receive() == 'LOCKED'


def test_locking_garbage_timeout(poolcounter, clients, lock_type):
    """Locking with garbage timeout LOCKs"""
    client = clients.get(1)
    client.send('%s l 1 1 garbage' % lock_type)
    assert client.receive() == 'LOCKED'


def test_same_lock_twice(poolcounter, clients, lock_type):
    """The same lock can be locked twice"""
    client = clients.get(1)
    client.send('%s l 2 2 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('%s l 2 2 1' % lock_type)
    assert client.receive() == 'LOCKED'


def test_same_lock_twice_timeout(poolcounter, clients, lock_type):
    """Locking the same lock twice produces TIMEOUT with non-zero timeout"""
    client = clients.get(1)
    client.send('%s l 1 2 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('%s l 1 2 1' % lock_type)
    assert client.receive() == 'TIMEOUT'


def test_same_lock_twice_zero_timeout(poolcounter, clients, lock_type):
    """Locking the same lock twice produces TIMEOUT with non-zero timeout"""
    client = clients.get(1)
    client.send('%s l 1 2 0' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('%s l 1 2 0' % lock_type)
    assert client.receive() == 'TIMEOUT'


def test_same_lock_twice_queue_full(poolcounter, clients, lock_type):
    """Locking the same lock twice produces QUEUE_FULL"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'QUEUE_FULL'


def test_timeout_doesnt_unlock(poolcounter, clients, lock_type):
    """Timing out doesn't unlock locks already held"""
    client = clients.get(1)
    client.send('%s l 1 2 1' % lock_type)
    assert client.receive() == 'LOCKED'
    client.send('%s l 1 2 0' % lock_type)
    assert client.receive() == 'TIMEOUT'
    client.send('%s l 1 2 0' % lock_type)
    assert client.receive() == 'TIMEOUT'
    client.send('RELEASE')
    assert client.receive() == 'RELEASED'


@pytest.mark.parametrize('timeout', [b'0', b'1'])
def test_timeout_doesnt_consume(poolcounter, clients, lock_type, timeout):
    """Timing out doesn't consume a connection's locks"""
    client = clients.get(1)
    client.send('%s l 1 2 %s' % (lock_type, timeout))
    assert client.receive() == 'LOCKED'
    for i in range(0, 6):
        client.send('%s l 1 2 %s' % (lock_type, timeout))
        assert client.receive() == 'TIMEOUT'


def test_no_queue_slots_not_consumed(poolcounter, clients, lock_type):
    """Running out of queue slots doesn't consume a connection's locks"""
    client = clients.get(1)
    client.send('%s l 1 1 1' % lock_type)
    assert client.receive() == 'LOCKED'
    for i in range(0, 6):
        client.send('%s l 1 1 1' % lock_type)
        assert client.receive() == 'QUEUE_FULL'


def test_release_not_consumed(poolcounter, clients, lock_type):
    """RELEASEing doesn't consume a connection's locks"""
    client = clients.get(1)
    for i in range(0, 7):
        client.send('%s l 1 1 1' % lock_type)
        assert client.receive() == 'LOCKED'
        client.send('RELEASE')
        assert client.receive() == 'RELEASED'


def test_disconnect_release(poolcounter, clients, lock_type):
    """Disconnecting releases locks and you can reconnect and get them back"""
    client = clients.get(1)
    client.send('%s l 1 10 1' % lock_type)
    assert client.receive() == 'LOCKED'
    # Disconnect client, reconnect anew
    client.close()
    client = clients.get(1)
    client.send('%s l 1 10 10' % lock_type)
    assert client.receive() == 'LOCKED'
