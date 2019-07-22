import sys

from asyncronous_com import utils
from asyncronous_com.server import Server


if __name__ == "__main__":

    filename = sys.argv[1]
    bind_url = sys.argv[2]
    remote_url = sys.argv[3]
    max_processes = int(sys.argv[4])
    ip_map = utils.server_data_to_hash_table(filename)
    if not ip_map:
        print("Either the file provided is empty or don't have rightly format lines")
    else:
        server = Server(identity='Server',
                        url=bind_url,
                        remote_url=remote_url,
                        max_processes=max_processes,
                        ip_map=ip_map)
        try:
            server.run()
        except KeyboardInterrupt:
            pass
        finally:
            server.clean()
