# server.py
import asyncio
import websockets
import numpy as np
from py_audio2face import Audio2Face
import threading
import queue
import json
import signal
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Initialize Audio2Face
a2f = Audio2Face()
a2f.init_a2f(streaming=True)
# Enable Live-Lynk streaming
try:
    payload = {
        "node_path": "/World/audio2face/StreamLivelink",
        "value": True
    }
    a2f.post("A2F/Exporter/ActivateStreamLivelink", payload)
    logging.info("Live-Lynk streaming activated")
except Exception as e:
    logging.error(f"Failed to activate Live-Lynk: {e}")
# Global variables to control the server
clients = set()
audio_queue = queue.Queue()
interrupt_event = threading.Event()
shutdown_event = threading.Event()

async def audio_handler(websocket):
    logging.info("Client connected")
    clients.add(websocket)
    try:
        samplerate = 24000  # Match the sample rate used in the React app

        while True:
            message = await websocket.recv()
            if isinstance(message, str):
                # Handle control messages (e.g., interruption)
                try:
                    msg = json.loads(message)
                    if msg.get('event') == 'interrupt':
                        # Handle interruption
                        logging.info("Interruption received")
                        interrupt_event.set()
                        # Clear the audio queue
                        with audio_queue.mutex:
                            audio_queue.queue.clear()
                    else:
                        logging.debug(f"Received unknown message: {msg}")
                except json.JSONDecodeError:
                    logging.warning(f"Received invalid JSON message: {message}")
            else:
                # Binary data (audio)
                # message is bytes
                float32_array = np.frombuffer(message, dtype=np.float32)
                # Put the data into the queue
                audio_queue.put(float32_array)
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")
    finally:
        clients.remove(websocket)
        # Signal the streaming thread to stop if no clients are connected
        if not clients:
            audio_queue.put(None)
            interrupt_event.set()
            shutdown_event.set()

def stream_audio_to_a2f():
    while not shutdown_event.is_set():
        # Wait until there is audio data to process
        try:
            data = audio_queue.get(timeout=1)
        except queue.Empty:
            continue
        if data is None:
            # End of stream or server shutting down
            logging.info("No audio data, waiting for new data...")
            continue  # Instead of breaking, we continue to wait for new data

        def audio_stream_generator(first_chunk):
            yield first_chunk
            while True:
                if interrupt_event.is_set():
                    # Handle interruption
                    logging.info("Interrupt event set, stopping audio stream")
                    interrupt_event.clear()
                    break
                try:
                    data = audio_queue.get(timeout=1)
                except queue.Empty:
                    continue
                if data is None:
                    # End of stream
                    logging.info("End of audio stream")
                    break
                yield data

        # Start streaming audio to A2F
        try:
            logging.info("Starting stream_audio to A2F")
            success = a2f.stream_audio(
                audio_stream=audio_stream_generator(data),
                samplerate=24000,
                block_until_playback_is_finished=True
            )
            logging.info(f"A2F streaming success: {success}")
        except Exception as e:
            logging.error(f"Error in stream_audio_to_a2f: {e}")

async def main():
    # Start the WebSocket server
    server = await websockets.serve(audio_handler, "localhost", 8765)
    logging.info("WebSocket server started on ws://localhost:8765")

    # Start the streaming thread
    streaming_thread = threading.Thread(
        target=stream_audio_to_a2f,
        daemon=True
    )
    streaming_thread.start()

    # Run the server until Ctrl+C is pressed
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    finally:
        shutdown_event.set()
        server.close()
        await server.wait_closed()
        logging.info("WebSocket server closed")
        streaming_thread.join()
        logging.info("Streaming thread terminated")

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
