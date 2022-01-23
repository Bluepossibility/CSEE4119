from socket import socket, AF_INET, SOCK_DGRAM, error as socket_error
from utils import not_corrupted  # Helper function
import argparse
import struct
import sys


"""python3 receiver.py -tcpserver localhost -file "output.txt" -listening_port 5002 -address_for_acks localhost  
-port_for_acks 5000"""

"""./newudpl -vv -p 5001 -i "localhost/*" -o localhost:5002"""


class Receiver:
    """
    Initiate Receiver
    (host, port) will be used to create a "TCP" Server Socket based on UDP,
    it receive information from new_udpl that is reading from sender.py
    (dst_host, dst_port) direct ACKs directly to "TCP" client, i.e. sender.py
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.dst_host = args.dst_host
        self.dst_port = args.dst_port
        self.socket = None
        self.ack = 0
        self.rcv_seq = 0
        self.FIN = 0  # Abbr of Finish, a FIN request to signal the end of the transmission.
        self.output_file = open(args.file, mode='w')

    # Run a while loop that will perform TCP receive, change status depending on FIN flag
    def Receive(self):
        try:
            self.socket = socket(AF_INET, SOCK_DGRAM)
        except socket_error as msg:
            print('Socket Creation Error: ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        try:
            self.socket.bind((self.host, self.port))
        except socket_error as msg:
            print('Socket Bind Error: ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        print("Server socket created and bind to host {} and port {}!".format(self.host, self.port))

        try:
            while True:
                # Receiver sends ACK regardless situation
                is_received = self.Receive_pkt()  # True if uncorrupted, in order packet is received

                if is_received:
                    self.ack = self.rcv_seq  # Send ack of received sequence number!
                    self.rcv_seq = 1 - self.rcv_seq  # Expecting next sequence number packet!

                else:
                    self.ack = 1-self.rcv_seq  # Send ack of previous sequence number!
                    self.rcv_seq = self.rcv_seq  # Expecting same sequence number packet!

                self.Send_ACK()

                if self.FIN == 1:
                    print("FIN received, closing the server......")
                    self.output_file.close()
                    raise KeyboardInterrupt


        except KeyboardInterrupt:
            self.socket.close()
            sys.exit()

    # This function is called whenever the server is ready to receive packets.
    def Receive_pkt(self):
        """
        Receive packets from sender, packet is consist of TCP_header and TCP_data in bytes
        :return: True or False, indicating whether packet is received not corrupted and in order
        """
        print("-------Receiving packets from sender-----------")
        bytes_pkt, _ = self.socket.recvfrom(2048)
        print('len(bytes_pkt): ', len(bytes_pkt))
        bytes_header = bytes_pkt[:20]
        bytes_data = bytes_pkt[20:]
        TCP_header = struct.unpack('HHIIBBHHH', bytes_header)
        seq = TCP_header[2]
        self.FIN = TCP_header[-4]
        data = bytes_data.decode("utf-8")
        print('TCP_header: ', TCP_header)
        if not_corrupted(TCP_header, data, is_from_sender=True):
            if seq == self.rcv_seq:
                print(data)
                self.write_data_to_txt(data)  # write data to output txt
                return True
            else:
                print("Packet has out of order sequence!")
                return False
        else:
            print("Data corrupted!")
            return False

    def Send_ACK(self):
        print('Sending ACK', self.ack)
        bytes_ACK = bytes('ACK{0}'.format(self.ack), 'utf-8')
        self.socket.sendto(bytes_ACK, (self.dst_host, self.dst_port))

    def write_data_to_txt(self, data):
        self.output_file.write(data)


# Main method to read command line arguments
def main():
    parser = argparse.ArgumentParser()
    # From command line get tcp server address
    parser.add_argument('-tcpserver', dest='host', action='store', required=True,
                        help='TCP server host that will listen to newudpl', type=str)
    # From command line get a file name which is the output directory
    parser.add_argument('-file', dest='file', action='store', required=True,
                        help='A file name indicating where to output', type=str)
    # From command line get listening port that will listen to newudpl, get data
    parser.add_argument('-listening_port', dest='port', action='store', required=True,
                        help='TCP server listening port that will listen to newudpl', type=int)
    # From command line get address sending ACKs to
    parser.add_argument('-address_for_acks', dest='dst_host', action='store', required=True,
                        help='Destination Host sending ACKs to', type=str)
    # From command line get port sending acks to
    parser.add_argument('-port_for_acks', dest='dst_port', action='store', required=True,
                        help='Destination port sending ACKs to', type=int)
    args = parser.parse_args()
    # Create Receiver and start listening
    receiver = Receiver(args)
    receiver.Receive()


if __name__ == "__main__":
    main()
