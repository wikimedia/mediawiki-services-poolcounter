import pytest
import subprocess


def test_garbage(poolcounter, clients):
    """Bad commands result in error"""
    client = clients.get(1)
    client.send('GARBAGE')
    assert client.receive() == 'ERROR BAD_COMMAND'


def test_locking_just_lockname(poolcounter, clients, lock_type):
    """locking with just lock name results in error"""
    client = clients.get(1)
    client.send('%s l' % lock_type)
    assert client.receive() == 'ERROR BAD_SYNTAX'


def test_locking_no_workers(poolcounter, clients, lock_type):
    """locking with no workers results in error"""
    client = clients.get(1)
    client.send('%s l 0 1 1' % lock_type)
    assert client.receive() == 'ERROR BAD_SYNTAX'


def test_locking_no_queue(poolcounter, clients, lock_type):
    """Locking with no queue results in error"""
    client = clients.get(1)
    client.send('%s l 1 0 1' % lock_type)
    assert client.receive() == 'ERROR BAD_SYNTAX'


def test_locking_non_integers(poolcounter, clients, lock_type):
    """Locking with no queue results in error"""
    client = clients.get(1)
    client.send('%s l GARBAGE 0 1' % lock_type)
    assert client.receive() == 'ERROR BAD_SYNTAX'


@pytest.mark.xfail  # flaky, sometimes timeouts in final recv
def test_locking_while_waiting(poolcounter, clients, lock_type):
    """Locking while waiting is an error"""
    client1, client2 = clients.get(2)
    client2.send('%s l 1 10 10' % lock_type)
    assert client2.receive() == 'LOCKED'
    client1.send('%s l 1 10 10' % lock_type)
    client1.send('%s l 1 10 10' % lock_type)
    assert client1.receive() == 'ERROR WAIT_FOR_RESPONSE'


def test_invalid_listen(poolcounter_path):
    with pytest.raises(subprocess.CalledProcessError) as e:
        subprocess.check_call([poolcounter_path, '-l', 'bad'])
    assert e.value.returncode == 1
