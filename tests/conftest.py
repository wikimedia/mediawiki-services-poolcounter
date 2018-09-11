import os
import pytest
import socket
import subprocess
import time

socket.setdefaulttimeout(5)


class ClientPool:
    """hands out Client instances and tears them down"""
    def __init__(self):
        self.local_ports = set()
        self.clients = set()

    def get(self, count):
        ret = []
        for i in range(1, count+1):
            try:
                local_port = self.local_ports.pop()
            except KeyError:
                local_port = 0
            client = Client(str(i), local_port)
            ret.append(client)
            self.clients.add(client)

        if count == 1:
            return ret[0]
        else:
            return ret

    def teardown(self):
        for client in self.clients:
            port = client.close()
            if port:
                # Recycle!
                self.local_ports.add(port)
        self.clients.clear()


class Client:
    """Wrapper around socket"""
    host = '127.0.0.1'
    port = 7531

    def __init__(self, name, local_port=0):
        self.name = name
        self.local_port = local_port
        self._socket = None

    @property
    def socket(self):
        if self._socket is None:
            tries = 5
            connected = False
            while not connected:
                self._socket = socket.socket()
                # TODO: is the getaddrinfo indirection necessary?
                remote = socket.getaddrinfo(self.host, self.port)
                local = socket.getaddrinfo(self.host, self.local_port)
                self._socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                try:
                    # We try and reuse the local port if we can. The only
                    # way to do that is is to bind on 0, copy the ephemeral
                    # port we're given, and then rebind on that the next
                    # time we open the socket.
                    self._socket.bind(local[0][4])
                    self._socket.connect(remote[0][4])
                    connected = True
                except (ConnectionRefusedError, OSError):
                    tries -= 1
                    if tries <= 0:
                        raise
                    # Wait for poolcounter to start?
                    time.sleep(2)
                    # else try again!

        return self._socket

    def send(self, command):
        print('%s -> ' % self.name + command)
        self.socket.send(command.encode() + b'\n')

    def receive(self):
        recv = self.socket.recv(4096).strip().decode()
        print('%s <- ' % self.name + recv)
        return recv

    def close(self):
        if self._socket:
            # Save the local_port for next time
            self.local_port = self._socket.getsockname()[1]
            # TODO: If _socket isn't connected, trying to shut
            # it down will error again
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self._socket = None
        return self.local_port


def find_poolcounterd():
    # env POOLCOUNTERD can point to the binary if you want to run tests
    # against an installed version
    path = os.environ.get(
        'POOLCOUNTERD',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'poolcounterd')
    )
    if not os.path.exists(path):
        pytest.skip('%s does not exist' % path)
    return path


@pytest.fixture(scope='session')
def poolcounter():
    path = find_poolcounterd()
    daemon = subprocess.Popen([path])
    yield daemon
    daemon.terminate()


@pytest.fixture()
def poolcounter_path():
    return find_poolcounterd()


# Use a singleton ClientPool to keep local_ports global
pool = ClientPool()


@pytest.fixture()
def clients():
    yield pool
    pool.teardown()


def pytest_generate_tests(metafunc):
    """parameterize lock_type if it's listed"""
    if 'lock_type' in metafunc.fixturenames:
        metafunc.parametrize('lock_type', ['ACQ4ME', 'ACQ4ANY'])
