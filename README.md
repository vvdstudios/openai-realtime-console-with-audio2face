# OpenAI Realtime Console with Audio2Face Integration

This project is a modified version of the OpenAI Realtime Console that integrates with NVIDIA's Audio2Face (A2F). It allows you to interact with an AI assistant in real-time while visualizing the assistant's responses through facial animations provided by A2F. The integration is achieved using a Python WebSocket server (`ws.py`) located in the `python-backend` folder.

<img src="/readme/realtime-console-demo.png" width="800" />

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Usage](#usage)
   - [Starting the Console](#starting-the-console)
   - [Interacting with the Assistant](#interacting-with-the-assistant)
4. [Configuration](#configuration)
   - [Using a Relay Server](#using-a-relay-server)
5. [Python Backend](#python-backend)
6. [Realtime API Reference Client](#realtime-api-reference-client)
   - [Sending Streaming Audio](#sending-streaming-audio)
   - [Adding and Using Tools](#adding-and-using-tools)
   - [Interrupting the Model](#interrupting-the-model)
   - [Reference Client Events](#reference-client-events)
7. [Wavtools](#wavtools)
   - [WavRecorder Quickstart](#wavrecorder-quickstart)
   - [WavStreamPlayer Quickstart](#wavstreamplayer-quickstart)
8. [Acknowledgments](#acknowledgments)
9. [License](#license)

---

## Introduction

This project extends the OpenAI Realtime Console by integrating it with NVIDIA's Audio2Face (A2F). It demonstrates how to stream audio data from a React application to A2F using a Python WebSocket server (`ws.py`), enabling real-time facial animations based on the assistant's spoken responses.

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher** (Python 3.11 recommended)
- **Node.js and npm** (for running the React application)
- **NVIDIA Omniverse Launcher**
- **NVIDIA Audio2Face Application**
- **Git** (for cloning the repository)

### Installation

1. **Clone the Repository**

   ```bash
   git clone git@github.com:vvdstudios/openai-realtime-console-with-audio2face.git
   cd openai-realtime-console-with-audio2face
   ```

2. **Set Up the Python Environment**

   Navigate to the `python-backend` folder:

   ```bash
   cd python-backend
   ```

   Create and activate a virtual environment:

   ```bash
   python -m venv venv
   'venv\Scripts\activate'
   ```

   Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` should include:

   ```
   py_audio2face
   websockets
   numpy
   ```

3. **Set Up the React Application**

   Navigate back to the root directory and install Node.js dependencies:

   ```bash
   cd ../
   npm install
   ```

---

## Usage

### Starting the Console

This is a React project created using `create-react-app` that is bundled via Webpack.

Start your server with:

```bash
npm start
```

The application should be available at `http://localhost:3000`.

### Interacting with the Assistant

The console requires an OpenAI API key (**user key** or **project key**) that has access to the Realtime API. You'll be prompted on startup to enter it. It will be saved via `localStorage` and can be changed at any time from the UI.

To start a session, you'll need to **connect**. This will require microphone access. You can then choose between **manual** (Push-to-talk) and **VAD** (Voice Activity Detection) conversation modes and switch between them at any time.

There are two functions enabled:

- **`get_weather`**: Ask for the weather anywhere, and the model will do its best to pinpoint the location, show it on a map, and get the weather for that location. Note that it doesn't have location access, and coordinates are "guessed" from the model's training data, so accuracy might not be perfect.
- **`set_memory`**: You can ask the model to remember information for you, and it will store it in a JSON blob on the right.

You can freely interrupt the model at any time in push-to-talk or VAD mode.

---

## Configuration


### Audio Configuration on Windows

It is important to have functional Audio Echo Cancellation (AEC) on the device running the samples to ensure clear audio playback and recording. 


1. **Open Control Panel**:
   - Press `Windows + R` to open the Run dialog.
   - Type `control` and press `Enter` to open the Control Panel.

2. **Navigate to Sound Settings**:
   - In the Control Panel, click on **Hardware and Sound**.
   - Click on **Sound** to open the Sound settings dialog.

3. **Select Recording Device**:
   - In the Sound settings window, navigate to the **Recording** tab.
   - Locate and e.g. select **Microphone Array** from the list of recording devices.
   - Click **Properties** to open the Microphone Properties dialog for the selected device.

4. **Enable Audio Enhancements**:
   - In the Microphone Properties dialog, navigate to the **Advanced** tab.
   - Under the **Signal Enhancements** section, look for the option labeled **Enable audio enhancements**.
   - Check the box next to **Enable audio enhancements** to allow extra signal processing by the audio device.

5. **Apply and Confirm Changes**:
   - Click **Apply** to save the changes.
   - Click **OK** to exit the Microphone Properties dialog.
   - Click **OK** in the Sound settings window to close it.


### Using a Relay Server

If you would like to build a more robust implementation and play around with the reference client using your own server, a Node.js Relay Server is included in the `relay-server` folder.

Start the relay server with:

```bash
npm run relay
```

It will start automatically on `localhost:8081`.

**You will need to create a `.env` file** with the following configuration:

```env
OPENAI_API_KEY=YOUR_API_KEY
REACT_APP_LOCAL_RELAY_SERVER_URL=http://localhost:8081
```

You will need to restart both your React app and relay server for the `.env` changes to take effect. The local server URL is loaded via [`ConsolePage.tsx`](/src/pages/ConsolePage.tsx):

```javascript
const LOCAL_RELAY_SERVER_URL: string =
  process.env.REACT_APP_LOCAL_RELAY_SERVER_URL || '';
```

To stop using the relay server at any time, simply delete the environment variable or set it to an empty string.

---

## Python Backend

The Python WebSocket server (`ws.py`) is located inside the `python-backend` folder. This server receives audio data from the React application and forwards it to Audio2Face (A2F) for real-time facial animation.

### Starting the Python Server

Navigate to the `python-backend` folder and run:

```bash
python ws.py
```

Ensure that Audio2Face is running and configured to accept streaming input.

---

## Realtime API Reference Client

The latest reference client and documentation are available on GitHub at [openai/openai-realtime-api-beta](https://github.com/openai/openai-realtime-api-beta).

You can use this client yourself in any React (front-end) or Node.js project. For full documentation, refer to the GitHub repository, but you can use the guide here as a primer to get started.

```javascript
import { RealtimeClient } from '/src/lib/realtime-api-beta/index.js';

const client = new RealtimeClient({ apiKey: process.env.OPENAI_API_KEY });

// Set parameters ahead of connecting
client.updateSession({ instructions: 'You are a great, upbeat friend.' });
client.updateSession({ voice: 'alloy' });
client.updateSession({ turn_detection: 'server_vad' });
client.updateSession({ input_audio_transcription: { model: 'whisper-1' } });

// Set up event handling
client.on('conversation.updated', ({ item, delta }) => {
  const items = client.conversation.getItems(); // can use this to render all items
  /* includes all changes to conversations, delta may be populated */
});

// Connect to Realtime API
await client.connect();

// Send an item and trigger a generation
client.sendUserMessageContent([{ type: 'text', text: `How are you?` }]);
```

### Sending Streaming Audio

To send streaming audio, use the `.appendInputAudio()` method. If you're in `turn_detection: 'disabled'` mode, then you need to use `.generate()` to tell the model to respond.

```javascript
// Send user audio; must be Int16Array or ArrayBuffer
// Default audio format is pcm16 with a sample rate of 24,000 Hz
for (let i = 0; i < 10; i++) {
  const data = new Int16Array(2400);
  for (let n = 0; n < 2400; n++) {
    const value = Math.floor((Math.random() * 2 - 1) * 0x8000);
    data[n] = value;
  }
  client.appendInputAudio(data);
}
// Pending audio is committed, and the model is asked to generate
client.createResponse();
```

### Adding and Using Tools

Working with tools is easy. Just call `.addTool()` and set a callback as the second parameter. The callback will be executed with the parameters for the tool, and the result will be automatically sent back to the model.

```javascript
// Add tools with callbacks specified
client.addTool(
  {
    name: 'get_weather',
    description:
      'Retrieves the weather for a given lat, lng coordinate pair. Specify a label for the location.',
    parameters: {
      type: 'object',
      properties: {
        lat: {
          type: 'number',
          description: 'Latitude',
        },
        lng: {
          type: 'number',
          description: 'Longitude',
        },
        location: {
          type: 'string',
          description: 'Name of the location',
        },
      },
      required: ['lat', 'lng', 'location'],
    },
  },
  async ({ lat, lng, location }) => {
    const result = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,wind_speed_10m`
    );
    const json = await result.json();
    return json;
  }
);
```

### Interrupting the Model

You may want to manually interrupt the model, especially in `turn_detection: 'disabled'` mode. To do this, use:

```javascript
// 'id' is the id of the item currently being generated
// 'sampleCount' is the number of audio samples that have been heard by the listener
client.cancelResponse(id, sampleCount);
```

This method will cause the model to immediately cease generation but also truncate the item being played by removing all audio after `sampleCount` and clearing the text response. By using this method, you can interrupt the model and prevent it from "remembering" anything it has generated that is ahead of where the user's state is.

### Reference Client Events

There are five main client events for application control flow in `RealtimeClient`. Note that this is only an overview of using the client; the full Realtime API event specification is considerably larger. For more control, check out the GitHub repository: [openai/openai-realtime-api-beta](https://github.com/openai/openai-realtime-api-beta).

```javascript
// Errors like connection failures
client.on('error', (event) => {
  // Handle error
});

// In VAD mode, the user starts speaking
// Use this to stop audio playback of a previous response if necessary
client.on('conversation.interrupted', () => {
  // Handle interruption
});

// Includes all changes to conversations
// 'delta' may be populated
client.on('conversation.updated', ({ item, delta }) => {
  // Get all items, e.g., if you need to update a chat window
  const items = client.conversation.getItems();
  switch (item.type) {
    case 'message':
      // System, user, or assistant message (item.role)
      break;
    case 'function_call':
      // Always a function call from the model
      break;
    case 'function_call_output':
      // Always a response from the user/application
      break;
  }
  if (delta) {
    // Only one of the following will be populated for any given event
    // delta.audio = Int16Array, audio added
    // delta.transcript = string, transcript added
    // delta.arguments = string, function arguments added
  }
});

// Triggered after item added to conversation
client.on('conversation.item.appended', ({ item }) => {
  // Item status can be 'in_progress' or 'completed'
});

// Triggered after item completed in conversation
// Always follows 'conversation.item.appended'
client.on('conversation.item.completed', ({ item }) => {
  // Item status will always be 'completed'
});
```

---

## Wavtools

The `wavtools` library provides easy management of PCM16 audio streams in the browser, both recording and playing. In this modified version, the `WavStreamPlayer` has been updated to send audio data over a WebSocket to the Python backend (`ws.py`) for integration with Audio2Face.

### WavRecorder Quickstart

```javascript
import { WavRecorder } from '/src/lib/wavtools/index.js';

const wavRecorder = new WavRecorder({ sampleRate: 24000 });
wavRecorder.getStatus(); // "ended"

// Request permissions and connect microphone
await wavRecorder.begin();
wavRecorder.getStatus(); // "paused"

// Start recording
// This callback will be triggered in chunks of 8192 samples by default
// 'mono' and 'raw' are Int16Array (PCM16) mono & full channel data
await wavRecorder.record((data) => {
  const { mono, raw } = data;
});
wavRecorder.getStatus(); // "recording"

// Stop recording
await wavRecorder.pause();
wavRecorder.getStatus(); // "paused"

// Output "audio/wav" audio file
const audio = await wavRecorder.save();

// Clear current audio buffer and start recording
await wavRecorder.clear();
await wavRecorder.record();

// Get data for visualization
const frequencyData = wavRecorder.getFrequencies();

// Stop recording, disconnect microphone, output file
await wavRecorder.pause();
const finalAudio = await wavRecorder.end();

// Listen for device changes; e.g., if a microphone is disconnected
// 'deviceList' is an array of MediaDeviceInfo[] with a 'default' property
wavRecorder.listenForDeviceChange((deviceList) => {});
```

### WavStreamPlayer Quickstart

In this modified version, the `WavStreamPlayer` has been updated to send the assistant's audio output over a WebSocket to the Python backend for processing with Audio2Face.

```javascript
import { WavStreamPlayer } from '/src/lib/wavtools/index.js';

// Create a WebSocket connection to the Python backend
const websocket = new WebSocket('ws://localhost:8765');
websocket.binaryType = 'arraybuffer';

// Instantiate WavStreamPlayer with the WebSocket
const wavStreamPlayer = new WavStreamPlayer({
  sampleRate: 24000,
  websocket: websocket,
});

// Connect to audio output
await wavStreamPlayer.connect();

// Handle WebSocket events
websocket.onopen = () => {
  console.log('WebSocket connected');
};

websocket.onclose = (event) => {
  console.log('WebSocket disconnected:', event);
};

websocket.onerror = (error) => {
  console.error('WebSocket error', error);
};

// Add audio data to the player
// The assistant's audio responses (Int16Array) are added here
wavStreamPlayer.add16BitPCM(audioData, 'assistant-response');

// The add16BitPCM method sends the audio data over WebSocket to the Python backend
// The backend then forwards the audio to Audio2Face for real-time animation

// Get data for visualization
const frequencyData = wavStreamPlayer.getFrequencies();

// Interrupt the audio (halt playback) at any time
// To restart, call '.add16BitPCM()' again
const trackOffset = await wavStreamPlayer.interrupt();
trackOffset.trackId;     // "assistant-response"
trackOffset.offset;      // Sample number
trackOffset.currentTime; // Time in track

// Send an interruption signal over WebSocket to the Python backend
await wavStreamPlayer.interrupt();
```

**Note:** In this modified version, the `WavStreamPlayer` class is updated to:

- Accept a `websocket` parameter during instantiation.
- Send audio data over the WebSocket connection in the `add16BitPCM` method.
- Send an interruption message over the WebSocket in the `interrupt` method.

**Example of Modified `add16BitPCM` Method:**

```javascript
add16BitPCM(arrayBuffer, trackId = 'default') {
  let buffer;
  if (arrayBuffer instanceof Int16Array) {
    buffer = arrayBuffer;
  } else if (arrayBuffer instanceof ArrayBuffer) {
    buffer = new Int16Array(arrayBuffer);
  } else {
    throw new Error(`Argument must be Int16Array or ArrayBuffer`);
  }

  // Send the audio data over WebSocket
  if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
    // Convert Int16Array to Float32Array and normalize to [-1.0, 1.0]
    const float32Array = new Float32Array(buffer.length);
    for (let i = 0; i < buffer.length; i++) {
      float32Array[i] = buffer[i] / 32768.0;
    }
    // Send the Float32Array buffer over WebSocket
    console.log('Sending audio data over WebSocket:', float32Array.length);
    this.websocket.send(float32Array.buffer);
  } else {
    console.warn('WebSocket is not open. Cannot send audio data.');
  }

  // Optionally, you can still play the audio locally if desired
  // this.queueAudio(buffer, trackId);
  return buffer;
}
```

---

## Acknowledgments

Special thanks to the OpenAI Realtime API team and NVIDIA for providing the tools and resources to make this integration possible.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
