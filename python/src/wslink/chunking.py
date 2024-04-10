import sys
import secrets
import msgpack
from typing import Dict, Tuple, Union
if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

UINT32_LENGTH = 4
ID_LOCATION = 0
ID_LENGTH = UINT32_LENGTH
MESSAGE_OFFSET_LOCATION = ID_LOCATION + ID_LENGTH
MESSAGE_OFFSET_LENGTH = UINT32_LENGTH
MESSAGE_SIZE_LOCATION = MESSAGE_OFFSET_LOCATION + MESSAGE_OFFSET_LENGTH
MESSAGE_SIZE_LENGTH = UINT32_LENGTH

HEADER_LENGTH = ID_LENGTH + MESSAGE_OFFSET_LENGTH + MESSAGE_SIZE_LENGTH


def _encode_header(id: bytes, offset: int, size: int) -> bytes:
    return (
        id
        + offset.to_bytes(MESSAGE_OFFSET_LENGTH, "little", signed=False)
        + size.to_bytes(MESSAGE_SIZE_LENGTH, "little", signed=False)
    )


def _decode_header(header: bytes) -> Tuple[bytes, int, int]:
    id = header[ID_LOCATION:ID_LENGTH]
    offset = int.from_bytes(
        header[
            MESSAGE_OFFSET_LOCATION : MESSAGE_OFFSET_LOCATION + MESSAGE_OFFSET_LENGTH
        ],
        "little",
        signed=False,
    )
    size = int.from_bytes(
        header[MESSAGE_SIZE_LOCATION : MESSAGE_SIZE_LOCATION + MESSAGE_SIZE_LENGTH],
        "little",
        signed=False,
    )
    return id, offset, size


def generate_chunks(message: bytes, max_size: int):
    total_size = len(message)

    if max_size == 0:
        max_content_size = total_size
    else:
        max_content_size = max(max_size - HEADER_LENGTH, 1)

    id = secrets.token_bytes(ID_LENGTH)

    offset = 0

    while offset < total_size:
        header = _encode_header(id, offset, total_size)
        chunk_content = message[offset : offset + max_content_size]

        yield header + chunk_content

        offset += max_content_size

    return


class PendingMessage(TypedDict):
    received_size: int
    content: bytearray


# This un-chunker is vulnerable to DOS.
# If it receives a message with a header claiming a large incoming message
# it will allocate the memory blindly even without actually receiving the content
# Chunks for a given message can come in any order
# Chunks across messages can be interleaved.
class UnChunker:
    pending_messages: Dict[bytes, PendingMessage]
    max_message_size: int

    def __init__(self):
        self.pending_messages = {}
        self.max_message_size = 512

    def set_max_message_size(self, size):
        self.max_message_size = size

    def release_pending_messages(self):
        self.pending_messages = {}

    def process_chunk(self, chunk: bytes) -> Union[bytes, None]:
        header, chunk_content = chunk[:HEADER_LENGTH], chunk[HEADER_LENGTH:]
        id, offset, total_size = _decode_header(header)

        pending_message = self.pending_messages.get(id, None)

        if pending_message is None:
            if total_size > self.max_message_size:
                raise ValueError(
                    f"""Total size for message {id} exceeds the allocation limit allowed.
    Maximum size = {self.max_message_size},
    Received size = {total_size}."""
                )

            pending_message = PendingMessage(
                received_size=0, content=bytearray(total_size)
            )
            self.pending_messages[id] = pending_message

        # This should never happen, but still check it
        if total_size != len(pending_message["content"]):
            del self.pending_messages[id]
            raise ValueError(
                f"Total size in chunk header for message {id} does not match total size declared by previous chunk."
            )

        content_size = len(chunk_content)
        content_view = memoryview(pending_message["content"])
        content_view[offset : offset + content_size] = chunk_content
        pending_message["received_size"] += content_size

        if pending_message["received_size"] >= total_size:
            full_message = pending_message["content"]
            del self.pending_messages[id]
            return msgpack.unpackb(bytes(full_message))

        return None


class StreamPendingMessage(TypedDict):
    received_size: int
    total_size: int
    unpacker: msgpack.Unpacker


# This un-chunker is more memory efficient
# (each chunk is passed immediately to msgpack)
# and it will only allocate memory when it receives content.
# Chunks for a given message are expected to come sequentially
# Chunks across messages can be interleaved.
class StreamUnChunker:
    pending_messages: Dict[bytes, StreamPendingMessage]

    def __init__(self):
        self.pending_messages = {}

    def set_max_message_size(self, _size):
        pass

    def release_pending_messages(self):
        self.pending_messages = {}

    def process_chunk(self, chunk: bytes) -> Union[bytes, None]:
        header, chunk_content = chunk[:HEADER_LENGTH], chunk[HEADER_LENGTH:]
        id, offset, total_size = _decode_header(header)

        pending_message = self.pending_messages.get(id, None)

        if pending_message is None:
            pending_message = StreamPendingMessage(
                received_size=0,
                total_size=total_size,
                unpacker=msgpack.Unpacker(max_buffer_size=total_size),
            )
            self.pending_messages[id] = pending_message

        # This should never happen, but still check it
        if offset != pending_message["received_size"]:
            del self.pending_messages[id]
            raise ValueError(
                f"""Received an unexpected chunk for message {id}.
    Expected offset = {pending_message['received_size']},
    Received offset = {offset}."""
            )

        # This should never happen, but still check it
        if total_size != pending_message["total_size"]:
            del self.pending_messages[id]
            raise ValueError(
                f"""Received an unexpected total size in chunk header for message {id}.
    Expected size = {pending_message['total_size']},
    Received size = {total_size}."""
            )

        content_size = len(chunk_content)
        pending_message["received_size"] += content_size

        unpacker = pending_message["unpacker"]
        unpacker.feed(chunk_content)

        full_message = None

        try:
            full_message = unpacker.unpack()
        except msgpack.OutOfData:
            pass  # message is incomplete, keep ingesting chunks

        if full_message is not None:
            del self.pending_messages[id]

            if pending_message["received_size"] < total_size:
                # In principle feeding a stream to the unpacker could yield multiple outputs
                # for example unpacker.feed(b'0123') would yield b'0', b'1', ect
                # or concatenated packed payloads would yield two or more unpacked objects
                # but in our use case we expect a full message to be mapped to a single object
                raise ValueError(
                    f"""Received a parsable payload shorter than expected for message {id}.
    Expected size = {total_size},
    Received size = {pending_message['received_size']}."""
                )

        return full_message
