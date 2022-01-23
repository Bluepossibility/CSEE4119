from socket import socket, AF_INET, SOCK_DGRAM, timeout, error as socket_error
from utils import MAX_PAYLOAD  # MAX_PAYLOAD is assigned 576
from utils import checksum  # Helper function
import argparse
import struct
import sys

""" python3 sender.py -tcpclient localhost -file "input.txt" -address_of_udpl localhost -port_number_of_udpl 5001 
-windowsize 8000 -ack_port_number 5000 < input.txt """


class Sender:

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.dst_host = args.dst_host
        self.dst_port = args.dst_port
        self.window_size = args.window_size
        self.socket = None
        self.seq = 0  # begin with 0
        self.buffer = []
        self.timeout = 2

    # Perform a while loop that will perform tcp send, change status depending on FIN, etc.
    def Send(self):
        """
            Initiate Sender
            (host, port) will be used to create a "TCP" client Socket based on UDP, send packets to newudpl
            (dst_host, dst_port) will be used to direct packets to newudpl
            The UDP client socket will receive ACK/NAK directly from receiver.py, i.e. "TCP" server
        """
        try:
            self.socket = socket(AF_INET, SOCK_DGRAM)
        except socket_error:
            print('Failed to create client socket')
            sys.exit()

        try:
            self.socket.bind((self.host, self.port))
        except socket_error:
            print('Bind failed')
            sys.exit()

        try:
            # sys.stdin is used for all interactive input (including calls to input());
            inf = sys.stdin
            current_payload = inf.read(MAX_PAYLOAD)

            # Read everything to the buffer
            while len(current_payload) > 0:
                # FIN, finish or not, False indicating not finished yet
                is_fin = False
                # If current_payload is less thant Max_payload, than this is the final batch of data
                if len(current_payload) < MAX_PAYLOAD:
                    is_fin = True
                self.buffer.append(self.DIY_TCP_pkt(current_payload, self.seq, is_fin=is_fin))
                current_payload = inf.read(MAX_PAYLOAD)
                self.seq = 1 - self.seq  # Sequence number oscillate between 0 and 1

            # Transmit everything in the buffer
            self.seq = 0
            index = 0
            while index < len(self.buffer):
                try:
                    while True:
                        print("Transmitting No.{} packet...".format(index))
                        is_send = self.Send_pkt(self.buffer[index])
                        if is_send:
                            break
                    self.socket.settimeout(self.timeout)

                    # Receive ACKs directly from "TCP" server
                    while True:
                        is_received = self.Receive_ACK()
                        if is_received:
                            self.seq = 1 - self.seq  # Sequence number oscillate between 0 and 1
                            break
                except timeout:
                    print("Timeout occurs! retransmit......")
                    self.socket.settimeout(None)
                    continue
                except socket_error as msg:
                    print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                    sys.exit()
                index += 1

        except KeyboardInterrupt:
            self.socket.close()
            sys.exit()

    def Receive_ACK(self):
        """
        Receive ACKs directly from receiver
        :return: True or False indicating whether ACK sequence is correct
        """
        bytes_ACK, _ = self.socket.recvfrom(2048)
        ACK = bytes_ACK.decode("utf-8")
        print('ACK received：', ACK)
        ACK_seq = ACK[-1]
        if ACK_seq == str(self.seq):
            print("Sender received ACK!")
            return True
        else:
            print('ACK seq received：', ACK_seq, 'while self.seq is: ', self.seq)
            print("ACK sequence is not correct!")
            return False

    def Send_pkt(self, pkt):
        self.socket.sendto(pkt, (self.dst_host, self.dst_port))
        return True

    # Call this function to create DIY TCP packet
    def DIY_TCP_pkt(self, data, seq, is_fin=False) -> bytes:
        """
           You need to implement the 20-byte TCP header format, without options.
           You do not have to implement push (PSH flag), urgent data (URG), reset (RST) or TCP options.
           You should set the port numbers in the packet to the right values, but can otherwise ignore them.
           The TCP checksum is computed over the TCP header and data (with the checksum set to zero);
           this does not quite correspond to the correct way of doing it (which includes parts of the IP header),
           but is close enough.
        """
        TCP_header = struct.pack(
            'HHIIBBHHH',  # H-2Bytes, I-4Bytes, B-1Bytes
            self.port,  # Source Port, H-2Bytes
            self.dst_port,  # Destination Port, H-2Bytes
            seq,  # Sequence Number, I-4Bytes
            0,  # ACK Number, I-4Bytes
            5 << 4,  # Data Offset, 80, B-1Bytes
            is_fin,  # Flags, B-1Bytes
            self.window_size,  # Window, H-2Bytes
            checksum(data),  # Checksum (initial value), H-2Bytes
            0  # Urgent pointer, H-2Bytes
        )
        bytes_data = bytes(data, 'utf-8')
        TCP_pkt = TCP_header + bytes_data

        return TCP_pkt


# Main method to read command line arguments
def main():
    parser = argparse.ArgumentParser()
    # From command line get tcp client address
    parser.add_argument('-tcpclient', dest='host', action='store', required=True,
                        help='Client host address that will send packets to newudpl', type=str)
    # From command line get a file name which is the input directory
    parser.add_argument('-file', dest='file', action='store', required=True,
                        help='A file name indicating where to input', type=str)
    # From command line get newudpl address sending packets to
    parser.add_argument('-address_of_udpl', dest='dst_host', action='store', required=True,
                        help='Destination newudpl address sending packets to', type=str)
    # From command line get newudpl port sending packets to
    parser.add_argument('-port_number_of_udpl', dest='dst_port', action='store', required=True,
                        help='Destination newudpl port sending packets to', type=int)
    # From command line get window size
    parser.add_argument('-windowsize', dest='window_size', action='store', required=True,
                        help='window size', type=int)
    # From command line get port for receiving ACKs
    parser.add_argument('-ack_port_number', dest='port', action='store', required=True,
                        help='Destination port for receiving ACKs', type=int)
    args = parser.parse_args()

    # Create sender object and send data
    sender = Sender(args)
    sender.Send()


if __name__ == "__main__":
    main()
