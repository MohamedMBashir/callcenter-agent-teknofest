from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import json
import base64
import tempfile
import os
from provider import GroqSTT

app = FastAPI(title="STT WebSocket Server")
stt = GroqSTT()

# web soketi hızlıca test etmek için fonksiyon
# @app.get("/")
# async def test_page():
#     """Simple test page"""
#     return HTMLResponse("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>STT Test</title>
#         <style>
#             body { font-family: Arial; padding: 40px; max-width: 600px; margin: auto; }
#             button { padding: 15px 30px; font-size: 18px; cursor: pointer; }
#             #output { margin-top: 20px; padding: 20px; background: #f0f0f0; min-height: 100px; }
#             .recording { background: #ff4444; color: white; }
#         </style>
#     </head>
#     <body>
#         <h1>STT Test</h1>
#         <button id="btn" onclick="toggleRecording()">Start Recording</button>
#         <div id="output"></div>
#
#         <script>
#             let ws = new WebSocket('ws://localhost:8000/transcribe');
#             let mediaRecorder;
#             let recording = false;
#
#             ws.onmessage = (e) => {
#                 const data = JSON.parse(e.data);
#                 document.getElementById('output').innerHTML +=
#                     `<p>${new Date().toLocaleTimeString()}: ${data.text || data.error}</p>`;
#             };
#
#             async function toggleRecording() {
#                 const btn = document.getElementById('btn');
#
#                 if (!recording) {
#                     const stream = await navigator.mediaDevices.getUserMedia({audio: true});
#                     mediaRecorder = new MediaRecorder(stream);
#                     const chunks = [];
#
#                     mediaRecorder.ondataavailable = e => chunks.push(e.data);
#                     mediaRecorder.onstop = () => {
#                         const blob = new Blob(chunks);
#                         const reader = new FileReader();
#                         reader.onloadend = () => {
#                             ws.send(JSON.stringify({
#                                 audio: reader.result.split(',')[1]
#                             }));
#                         };
#                         reader.readAsDataURL(blob);
#                         stream.getTracks().forEach(t => t.stop());
#                     };
#
#                     mediaRecorder.start();
#                     btn.textContent = 'Stop Recording';
#                     btn.classList.add('recording');
#                     recording = true;
#                 } else {
#                     mediaRecorder.stop();
#                     btn.textContent = 'Start Recording';
#                     btn.classList.remove('recording');
#                     recording = false;
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """)


@app.websocket("/transcribe")
async def transcribe_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Speech-to-Text

    Expected message format:
    {
        "audio": "base64_encoded_audio"
    }

    Response format:
    {
        "text": "transcribed text"
    } or {
        "error": "error message"
    }
    """
    await websocket.accept()
    print("Client connected")

    while True:
        try:
            # Receive message
            message = await websocket.receive_text()
            data = json.loads(message)

            # Extract audio data
            audio_base64 = data.get("audio")
            if not audio_base64:
                await websocket.send_json({"error": "No audio data received"})
                continue

            # Decode base64 to bytes
            audio_bytes = base64.b64decode(audio_base64)
            print(f"Received audio: {len(audio_bytes)} bytes")

            # Save to temporary file (Groq API requires a file)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Transcribe with stt model
            try:
                text = stt.transcribe(temp_path)
                print(f"Transcription: {text}")

                # Send response
                await websocket.send_json({"text": text})

            except Exception as e:
                error_msg = str(e)
                print(f"Transcription error: {error_msg}")
                await websocket.send_json({"error": error_msg})

            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            print(f"WebSocket error: {e}")
            break

    print("Client disconnected")


if __name__ == "__main__":
    print("STT WebSocket Server")
    print("WebSocket: ws://localhost:8000/transcribe")
    print("Test UI: http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000)
