import pytest
import socket


def test_both_lock(poolcounter, clients, lock_type):
    """Both lock if there are enough workers and enough queue space"""
    client1, client2 = clients.get(2)
    client1.send('%s l 2 2 1' % lock_type)
    assert client1.receive() == 'LOCKED'
    client2.send('%s l 2 2 1' % lock_type)
    assert client2.receive() == 'LOCKED'


def test_only_one_lock_no_queue_space(poolcounter, clients, lock_type):
    """Only one can lock if there are enough workers but not enough
    queue space"""
    client1, client2 = clients.get(2)
    client1.send('%s l 2 1 1' % lock_type)
    assert client1.receive() == 'LOCKED'
    client2.send('%s l 2 1 1' % lock_type)
    assert client2.receive() == 'QUEUE_FULL'


def test_only_one_lock_no_workers_nor_queue_space(
        poolcounter, clients, lock_type):
    """Only one can lock if there aren't workers and not enough queue space"""
    client1, client2 = clients.get(2)
    client1.send('%s l 1 1 1' % lock_type)
    assert client1.receive() == 'LOCKED'
    client2.send('%s l 1 1 1' % lock_type)
    assert client2.receive() == 'QUEUE_FULL'


def test_close_socket_release(poolcounter, clients):
    """Closing a socket releases the lock"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ANY l 2 1 1')
    assert client1.receive() == 'LOCKED'
    # Close client1
    client1.close()
    client2.send('ACQ4ANY l 2 1 1')
    assert client2.receive() == 'LOCKED'


def test_second_timeout_gt_zero(poolcounter, clients):
    """Second client TIMEOUTs if first never unlocks and timeout > 0"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 1')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 2 1')
    assert client2.receive() == 'TIMEOUT'


def test_second_timeout_eq_zero(poolcounter, clients):
    """Second client TIMEOUTs if first never unlocks and timeout == 0"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 0')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 2 0')
    assert client2.receive() == 'TIMEOUT'


def test_second_timeout_after_first_finish(poolcounter, clients):
    """Second client TIMEOUTs if first never unlocks but can get lock
    after first finishes"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 1')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 2 1')
    assert client2.receive() == 'TIMEOUT'
    client2.send('ACQ4ME l 1 2 1')
    assert client2.receive() == 'TIMEOUT'
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    client2.send('ACQ4ME l 1 2 1')
    assert client2.receive() == 'LOCKED'


def test_second_timeout_after_first_finish_zero_timeout(poolcounter, clients):
    """Second client TIMEOUTs if first never unlocks but can get lock
    after first finishes and timeout == 0"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 0')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 2 0')
    assert client2.receive() == 'TIMEOUT'
    client2.send('ACQ4ME l 1 2 0')
    assert client2.receive() == 'TIMEOUT'
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    client2.send('ACQ4ME l 1 2 0')
    assert client2.receive() == 'LOCKED'


def test_second_lock_first_unlock(poolcounter, clients):
    """Second client's ACQ4ME LOCKs if first unlocks"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 2 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'LOCKED'


def test_second_lock_first_unlock_any(poolcounter, clients):
    """Second client's ACQ4ANY DONEs if first unlocks"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ANY l 1 2 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 2 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'


def test_done_no_unlock(poolcounter, clients):
    """DONE doesn't require unlock"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 2 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 2 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'
    client1.send('ACQ4ME l 1 2 5')
    assert client1.receive() == 'LOCKED'


def test_done_no_consume_lock(poolcounter, clients):
    """DONE doesn't consume a lock"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 5 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 5 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'
    client1.send('ACQ4ME l 1 5 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 5 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'
    client1.send('ACQ4ME l 1 5 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 5 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'
    client1.send('ACQ4ME l 1 5 5')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ANY l 1 5 5')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'DONE'
    client2.send('ACQ4ME l 1 2 5')
    assert client2.receive() == 'LOCKED'


def test_lock_twice_multiple_executors(poolcounter, clients, lock_type):
    """locking the same lock twice takes multiple executors"""
    client1, client2 = clients.get(2)
    client1.send('%s l 2 2 0' % lock_type)
    assert client1.receive() == 'LOCKED'
    client1.send('%s l 2 2 0' % lock_type)
    assert client1.receive() == 'LOCKED'
    client2.send('%s l 2 2 0' % lock_type)
    assert client2.receive() == 'QUEUE_FULL'


def test_disconnect_while_timeout(poolcounter, clients, lock_type):
    """Disconnecting while waiting for a timeout is ok"""
    client1, client2 = clients.get(2)
    client1.send('%s l 1 10 1' % lock_type)
    assert client1.receive() == 'LOCKED'
    client2.send('%s l 1 10 10' % lock_type)
    client2.close()
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'


def test_no_timeout_after_initial_delay(poolcounter, clients):
    """Do not get timeout after locking after initial delay"""
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 10 1')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 10 3')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'LOCKED'
    # assert no response
    with pytest.raises(socket.timeout):
        client2.receive()


def test_no_early_timeout_after_initial_delay(poolcounter, clients):
    """
    Do not get early timeout after initial delay

    The "gets not response" here is within 5 seconds, meaning the
    timeout doesn't come early
    """
    client1, client2 = clients.get(2)
    client1.send('ACQ4ME l 1 10 1')
    assert client1.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 10 3')
    client1.send('RELEASE')
    assert client1.receive() == 'RELEASED'
    assert client2.receive() == 'LOCKED'
    client2.send('ACQ4ME l 1 10 10')
    # assert no response
    with pytest.raises(socket.timeout):
        client2.receive()
