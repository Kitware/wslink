// Project not setup for typescript, manually compiling this file to chunker.js
// npx tsc chunking.ts --target esnext

const UINT32_LENGTH = 4;
const ID_LOCATION = 0;
const ID_LENGTH = UINT32_LENGTH;
const MESSAGE_OFFSET_LOCATION = ID_LOCATION + ID_LENGTH;
const MESSAGE_OFFSET_LENGTH = UINT32_LENGTH;
const MESSAGE_SIZE_LOCATION = MESSAGE_OFFSET_LOCATION + MESSAGE_OFFSET_LENGTH;
const MESSAGE_SIZE_LENGTH = UINT32_LENGTH;

const HEADER_LENGTH = ID_LENGTH + MESSAGE_OFFSET_LENGTH + MESSAGE_SIZE_LENGTH;

function encodeHeader(id: number, offset: number, size: number): Uint8Array {
  const buffer = new ArrayBuffer(HEADER_LENGTH);
  const header = new Uint8Array(buffer);
  const view = new DataView(buffer);
  view.setUint32(ID_LOCATION, id, true);
  view.setUint32(MESSAGE_OFFSET_LOCATION, offset, true);
  view.setUint32(MESSAGE_SIZE_LOCATION, size, true);

  return header;
}

function decodeHeader(header: Uint8Array) {
  const view = new DataView(header.buffer);
  const id = view.getUint32(ID_LOCATION, true);
  const offset = view.getUint32(MESSAGE_OFFSET_LOCATION, true);
  const size = view.getUint32(MESSAGE_SIZE_LOCATION, true);

  return { id, offset, size };
}

function* generateChunks(message: Uint8Array, maxSize: number) {
  const totalSize = message.byteLength;
  let maxContentSize: number;

  if (maxSize === 0) {
    maxContentSize = totalSize;
  } else {
    maxContentSize = Math.max(maxSize - HEADER_LENGTH, 1);
  }

  const id = new Uint32Array(1);
  crypto.getRandomValues(id);

  let offset = 0;

  while (offset < totalSize) {
    const contentSize = Math.min(maxContentSize, totalSize - offset);
    const chunk = new Uint8Array(new ArrayBuffer(HEADER_LENGTH + contentSize));
    const header = encodeHeader(id[0], offset, totalSize);
    chunk.set(new Uint8Array(header.buffer), 0);
    chunk.set(message.subarray(offset, offset + contentSize), HEADER_LENGTH);

    yield chunk;

    offset += contentSize;
  }

  return;
}

type PendingMessage = {
  receivedSize: number;
  content: Uint8Array;
  decoder: any;
};

/*
  This un-chunker is vulnerable to DOS.
  If it receives a message with a header claiming a large incoming message
  it will allocate the memory blindly even without actually receiving the content
  Chunks for a given message can come in any order
  Chunks across messages can be interleaved.
*/
class UnChunker {
  private pendingMessages: { [key: number]: PendingMessage };

  constructor() {
    this.pendingMessages = {};
  }

  releasePendingMessages() {
    this.pendingMessages = {};
  }

  async processChunk(
    chunk: Blob,
    decoderFactory: () => any
  ): Promise<unknown | undefined> {
    const headerBlob = chunk.slice(0, HEADER_LENGTH);
    const contentBlob = chunk.slice(HEADER_LENGTH);

    const header = new Uint8Array(await headerBlob.arrayBuffer());
    const { id, offset, size: totalSize } = decodeHeader(header);

    let pendingMessage = this.pendingMessages[id];

    if (!pendingMessage) {
      pendingMessage = {
        receivedSize: 0,
        content: new Uint8Array(totalSize),
        decoder: decoderFactory(),
      };

      this.pendingMessages[id] = pendingMessage;
    }

    // This should never happen, but still check it
    if (totalSize !== pendingMessage.content.byteLength) {
      delete this.pendingMessages[id];
      throw new Error(
        `Total size in chunk header for message ${id} does not match total size declared by previous chunk.`
      );
    }

    const chunkContent = new Uint8Array(await contentBlob.arrayBuffer());
    const content = pendingMessage.content;
    content.set(chunkContent, offset);
    pendingMessage.receivedSize += chunkContent.byteLength;

    if (pendingMessage.receivedSize >= totalSize) {
      delete this.pendingMessages[id];

      try {
        return pendingMessage['decoder'].decode(content);
      } catch (e) {
        console.error('Malformed message: ', content.slice(0, 100));
        // debugger;
      }
    }

    return undefined;
  }
}

type StreamPendingMessage = {
  receivedSize: number;
  totalSize: number;
  decoder: any;
};

// Makes sure messages are processed in order of arrival,
export class SequentialTaskQueue {
  taskId: number;
  pendingTaskId: number;
  tasks: {
    [id: number]: {
      fn: (...args: any) => Promise<any>;
      args: any[];
      resolve: (value: any) => void;
      reject: (err: any) => void;
    };
  };

  constructor() {
    this.taskId = 0;
    this.pendingTaskId = -1;
    this.tasks = {};
  }

  enqueue(fn: (...args: any) => Promise<any>, ...args: any[]) {
    return new Promise((resolve, reject) => {
      const taskId = this.taskId++;
      this.tasks[taskId] = { fn, args, resolve, reject };
      this._maybeExecuteNext();
    });
  }

  _maybeExecuteNext() {
    let pendingTask = this.tasks[this.pendingTaskId];

    if (pendingTask) {
      return;
    }

    const nextPendingTaskId = this.pendingTaskId + 1;

    pendingTask = this.tasks[nextPendingTaskId];

    if (!pendingTask) {
      return;
    }

    this.pendingTaskId = nextPendingTaskId;

    const { fn, args, resolve, reject } = pendingTask;

    fn(...args)
      .then((result) => {
        resolve(result);
        delete this.tasks[nextPendingTaskId];
        this._maybeExecuteNext();
      })
      .catch((err) => {
        reject(err);
        delete this.tasks[nextPendingTaskId];
        this._maybeExecuteNext();
      });
  }
}

/*
  This un-chunker is more memory efficient
  (each chunk is passed immediately to msgpack)
  and it will only allocate memory when it receives content.
  Chunks for a given message are expected to come sequentially
  Chunks across messages can be interleaved.
*/
class StreamUnChunker {
  private pendingMessages: { [key: number]: StreamPendingMessage };

  constructor() {
    this.pendingMessages = {};
  }

  processChunk = async (
    chunk: Blob,
    decoderFactory: () => any
  ): Promise<unknown | undefined> => {
    const headerBlob = chunk.slice(0, HEADER_LENGTH);

    const header = new Uint8Array(await headerBlob.arrayBuffer());
    const { id, offset, size: totalSize } = decodeHeader(header);

    const contentBlob = chunk.slice(HEADER_LENGTH);

    let pendingMessage = this.pendingMessages[id];

    if (!pendingMessage) {
      pendingMessage = {
        receivedSize: 0,
        totalSize: totalSize,
        decoder: decoderFactory(),
      };

      this.pendingMessages[id] = pendingMessage;
    }

    // This should never happen, but still check it
    if (totalSize !== pendingMessage.totalSize) {
      delete this.pendingMessages[id];
      throw new Error(
        `Total size in chunk header for message ${id} does not match total size declared by previous chunk.`
      );
    }

    // This should never happen, but still check it
    if (offset !== pendingMessage.receivedSize) {
      delete this.pendingMessages[id];
      throw new Error(
        `Received an unexpected chunk for message ${id}.
           Expected offset = ${pendingMessage.receivedSize},
           Received offset = ${offset}.`
      );
    }

    let result: unknown;
    try {
      result = await pendingMessage.decoder.decodeAsync(
        contentBlob.stream() as any
      );
    } catch (e) {
      if (e instanceof RangeError) {
        // More data is needed, it should come in the next chunk
        result = undefined;
      }
    }

    pendingMessage.receivedSize += contentBlob.size;

    /*
      In principle feeding a stream to the unpacker could yield multiple outputs
      for example unpacker.feed(b'0123') would yield b'0', b'1', ect
      or concatenated packed payloads would yield two or more unpacked objects
      but in our use case we expect a full message to be mapped to a single object
    */
    if (result && pendingMessage.receivedSize < totalSize) {
      delete this.pendingMessages[id];
      throw new Error(
        `Received a parsable payload shorter than expected for message ${id}.
           Expected size = ${totalSize},
           Received size = ${pendingMessage.receivedSize}.`
      );
    }

    if (pendingMessage.receivedSize >= totalSize) {
      delete this.pendingMessages[id];
    }

    return result;
  };
}

export { UnChunker, StreamUnChunker, generateChunks };
