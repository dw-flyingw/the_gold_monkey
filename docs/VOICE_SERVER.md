# Running the Salty Voice Server on a Different Computer

This guide explains how to run the Salty voice server (`mcp_servers/voice_server.py`) on a separate machine from the main Salty app. This is useful if you want to offload audio processing or use a dedicated device for voice synthesis.

---

## 1. Prerequisites

- **Python 3.8+** installed on the target machine
- All dependencies installed (see `pyproject.toml` or `requirements.txt`)
- Access to your ElevenLabs API key (and any other required .env values)
- Network connectivity between the main app and the voice server machine

---

## 2. Copy the Codebase

Clone or copy the Salty project directory to the target machine:

```sh
git clone <your-repo-url> /path/to/Salty
cd /path/to/Salty
```

Or copy the relevant files via SCP, rsync, or file share.

---

## 3. Set Up the `.env` File

- Copy your `.env` file from the main app to the voice server machine.
- **Edit the following variables as needed:**

```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
VOICE_SERVER_URL=http://<voice-server-ip>:9006
TTS_METHOD=elevenlabs
```

- Make sure the API key and voice ID are valid for the new environment.

---

## 4. Copy the Audio Folder

**Important:** The voice server needs access to the `audio/` folder for parrot sound effects (squawk.wav, screeech.wav, etc.). Copy the entire `audio/` directory to the voice server machine:

```sh
# From the main app machine:
scp -r audio/ user@voice-server:/path/to/Salty/
# or
rsync -av audio/ user@voice-server:/path/to/Salty/audio/
```

The voice server expects the audio files to be in the same relative path structure as the main app.

---

## 5. Install Dependencies

On the voice server machine:

```sh
pip install -r requirements.txt
# or, if using poetry or uv:
# poetry install
# uv pip install -r requirements.txt
```

---

## 6. Run the Voice Server

On the voice server machine:

```sh
python mcp_servers/voice_server.py
```

You should see log output indicating the server is running, e.g.:

```
Uvicorn running on http://0.0.0.0:9006 (Press CTRL+C to quit)
```

---

## 7. Network/Firewall Notes

- The voice server listens on port **9006** by default. Make sure this port is open on the server's firewall.
- The main app must be able to reach `http://<voice-server-ip>:9006` over the network.
- If running on a local network, use the server's LAN IP address in `VOICE_SERVER_URL`.
- For remote/cloud servers, consider using a VPN or secure tunnel.

---

## 8. Point the Main App to the Remote Voice Server

On the main app machine, set in your `.env`:

```
VOICE_SERVER_URL=http://<voice-server-ip>:9006
```

Restart the main app. It will now send voice requests to the remote server.

---

## 9. Troubleshooting

- **Cannot connect:**
  - Check that the server is running and listening on the correct IP/port.
  - Check firewall settings on both machines.
  - Try `curl http://<voice-server-ip>:9006/available_voices` from the main app machine.
- **Audio not playing:**
  - Check logs for errors about audio device or missing dependencies.
  - Make sure the server has access to the required audio files.
- **ElevenLabs errors:**
  - Double-check your API key and voice ID in the `.env` file.
  - Check for network issues or API rate limits.
- **.env not loading:**
  - Make sure the `.env` file is present and readable on the server.

---

## 10. Security Notes

- Do not expose the voice server to the public internet without authentication.
- For production, consider running behind a VPN, SSH tunnel, or reverse proxy with access controls.

---

## 11. Example: Running on a Raspberry Pi

1. Set up Python and dependencies as above.
2. Copy `.env` and audio files:
   ```sh
   scp .env pi@raspberry-pi:/path/to/Salty/
   scp -r audio/ pi@raspberry-pi:/path/to/Salty/
   ```
3. Run the server:
   ```sh
   python mcp_servers/voice_server.py
   ```
4. Set `VOICE_SERVER_URL` in the main app to the Pi's IP.

---

For further help, see the main `README.md` or contact the project maintainer. 