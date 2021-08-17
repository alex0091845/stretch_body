from __future__ import print_function
import stretch_body.transport as transport
from stretch_body.transport import cobs_encoder as encoder
import time
import array

# methods
RPC_START_NEW_RPC =100
RPC_ACK_NEW_RPC= 101
RPC_SEND_BLOCK_MORE = 102
RPC_ACK_SEND_BLOCK_MORE = 103
RPC_SEND_BLOCK_LAST = 104
RPC_ACK_SEND_BLOCK_LAST = 105
RPC_GET_BLOCK = 106
RPC_ACK_GET_BLOCK_MORE = 107
RPC_ACK_GET_BLOCK_LAST = 108

# other
RPC_BLOCK_SIZE = 32
RPC_DATA_SIZE = 1024
READ_TIMEOUT = 0.2 # seconds
PACKET_MARKER = 0


def send(usb, rpc_type, ack_type, rpc_struct, ack_struct, rpc_arguments):
    if usb not in transport.buses:
        transport.logger.debug('Transport not open on: {0}'.format(usb))
        return False

    # initiate a new RPC
    encoded_buffer = encoder.frame(data=[RPC_START_NEW_RPC])
    transport.buses[usb].write(encoded_buffer)
    buffer, _ = _receive(usb)
    if buffer[0] != RPC_ACK_NEW_RPC:
        transport.logger.error('Transport receive error on: RPC_ACK_NEW_RPC')
        return False

    # # send rpc arguments as data blocks
    # something = [0] * 32
    # for i in range(0, len(something), RPC_BLOCK_SIZE):
    #     pass

    return True


def _receive(usb):
    start = time.time()
    rx_buffer = []
    while (time.time() - start) < READ_TIMEOUT:
        nn = transport.buses[usb].in_waiting
        waiting_bytes = transport.buses[usb].read(nn) if nn > 0 else []
        for byte in waiting_bytes:
            if type(byte) == str: # Py2 needs this, Py3 not
                byte = struct.unpack('B', byte)[0]
            if byte == PACKET_MARKER:
                buffer, size = encoder.deframe(encoded_data=rx_buffer)
                return buffer, size
            else:
                rx_buffer.append(byte)