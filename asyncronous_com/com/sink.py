import zmq

from asyncronous_com import errors
from asyncronous_com.com import pull_peer


class Sink(pull_peer.PullPeer):
    '''Sink End Peer using a Pull socket
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.socket.bind(self.url)
        except zmq.error.ZMQError as ex:
            raise errors.PushPullError(f"Unable to bind PULL socket with url {self.url}. "
                                       f"Ensure that the type of url and socket are the correct ones") from ex
