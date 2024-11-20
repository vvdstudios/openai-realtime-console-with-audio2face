// wav_stream_player.js
import { AudioAnalysis } from './analysis/audio_analysis.js';

/**
 * Handles audio data and sends it over WebSocket to the server.
 * @class
 */
export class WavStreamPlayer {
  /**
   * Creates a new WavStreamPlayer instance
   * @param {{sampleRate?: number, websocket?: WebSocket}} options
   * @returns {WavStreamPlayer}
   */
  constructor({ sampleRate = 44100, websocket = null } = {}) {
    this.sampleRate = sampleRate;
    this.websocket = websocket;
    this.analyser = null;
    this.trackSampleOffsets = {};
    this.interruptedTrackIds = {};
  }

  /**
   * Initializes the analyser for visualization (if needed).
   * @returns {Promise<true>}
   */
  async connect() {
    // Set up an AudioContext for visualization purposes
    this.context = new AudioContext({ sampleRate: this.sampleRate });
    if (this.context.state === 'suspended') {
      await this.context.resume();
    }
    const analyser = this.context.createAnalyser();
    analyser.fftSize = 8192;
    analyser.smoothingTimeConstant = 0.1;
    this.analyser = analyser;
    return true;
  }

  /**
   * Gets the current frequency domain data for visualization.
   * @param {"frequency"|"music"|"voice"} [analysisType]
   * @param {number} [minDecibels] default -100
   * @param {number} [maxDecibels] default -30
   * @returns {import('./analysis/audio_analysis.js').AudioAnalysisOutputType}
   */
  getFrequencies(
    analysisType = 'frequency',
    minDecibels = -100,
    maxDecibels = -30
  ) {
    if (!this.analyser) {
      throw new Error('Not connected, please call .connect() first');
    }
    return AudioAnalysis.getFrequencies(
      this.analyser,
      this.sampleRate,
      null,
      analysisType,
      minDecibels,
      maxDecibels
    );
  }

  /**
   * Sends 16-bit PCM audio data over WebSocket to the server.
   * @param {ArrayBuffer|Int16Array} arrayBuffer
   * @param {string} [trackId]
   * @returns {Int16Array}
   */
  add16BitPCM(arrayBuffer, trackId = 'default') {
    if (typeof trackId !== 'string') {
      throw new Error(`trackId must be a string`);
    } else if (this.interruptedTrackIds[trackId]) {
      return;
    }
    let buffer;
    if (arrayBuffer instanceof Int16Array) {
      buffer = arrayBuffer;
    } else if (arrayBuffer instanceof ArrayBuffer) {
      buffer = new Int16Array(arrayBuffer);
    } else {
      throw new Error(`argument must be Int16Array or ArrayBuffer`);
    }

    // Send the audio data over WebSocket
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      // Convert Int16Array to Float32Array and normalize to [-1.0, 1.0]
      const float32Array = new Float32Array(buffer.length);
      for (let i = 0; i < buffer.length; i++) {
        float32Array[i] = buffer[i] / 32768.0;
      }
      // Send the Float32Array buffer over WebSocket
      this.websocket.send(float32Array.buffer);
    }

    return buffer;
  }

  /**
   * Handles interruption by sending a message over WebSocket.
   * @returns {Promise<null>}
   */
  async interrupt() {
    // Send interruption message
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({ event: 'interrupt' }));
    }
    return null;
  }
}
