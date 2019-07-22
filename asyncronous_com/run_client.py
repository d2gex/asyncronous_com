import sys

from asyncronous_com import utils
from asyncronous_com.client import Client


if __name__ == "__main__":

    filename = sys.argv[1]
    group_member_num = int(sys.argv[2])
    bind_url = sys.argv[3]
    remote_url = sys.argv[4]
    tasks = utils.client_group_tasks(filename, group_member_num)
    if not tasks:
        print("Either the file provided is empty or don't have rightly format lines")
    else:
        client = Client(tasks)
        client.init_sink(identity='client_sink', url=bind_url)
        client.init_producer(identity='client_producer', url=remote_url)
        try:
            client.run()
        except KeyboardInterrupt:
            pass
        finally:
            if client.results:
                print(sum(client.results))
            else:
                print("Not results were fetched")
            client.clean()
