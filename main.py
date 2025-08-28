import pyaudio
import numpy as np
import pyrubberband as pyrb
import subprocess
import signal
import sys

app = pyaudio.PyAudio()

WORKING_APP = True
APP_VOICE_CHANGER = "alsa_playback.python3.12"
APP_DISCORD_NAME = "WEBRTC VoiceEngine"
MIC_DEVICE = ""
HEAD_PHONE_DEVICE = ""
SHIFT_VOICE_PITCH = -3

RATE = 48000
CHUNK = int( RATE * 0.5 )
CHANELS = 1

result = subprocess.run(["pw-link", "-l"], capture_output=True, text=True).stdout.splitlines()
for line in result:
    if not line.startswith(' '):
        if "alsa_input" in line:
            MIC_DEVICE = line[:-len(":captureAAA")]
        elif "alsa_output" in line:
            HEAD_PHONE_DEVICE = line[:-len(":playbackAAA")]

microSteam = app.open(format=pyaudio.paInt16, channels=CHANELS, rate=RATE, input=True, frames_per_buffer=CHUNK )
outputStream = app.open(format=pyaudio.paInt16, channels=CHANELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

def createTupleDevice(device, type):
    return (f"{device}:{type}_FL", f"{device}:{type}_FR")

microProvider = createTupleDevice(MIC_DEVICE, "capture")
headPhoneDevice = createTupleDevice(HEAD_PHONE_DEVICE, "playback")
changeVoiceOutput = createTupleDevice(APP_VOICE_CHANGER, "output")
discordDevice = createTupleDevice(APP_DISCORD_NAME, "input")

disconnectionPairFL = list(zip(microProvider, discordDevice))+list(zip(changeVoiceOutput, headPhoneDevice))
connectionList = list(zip(changeVoiceOutput, discordDevice))
bringConnectBackList = list(zip(microProvider, discordDevice))

for outPut, inPut in disconnectionPairFL:
    subprocess.run([ "pw-link", "-d", outPut, inPut ])

for outPut, inPut in connectionList:
    subprocess.run([ "pw-link", "-L", outPut, inPut ])

def handleKill(signum, frame):
    global WORKING_APP
    for outDev, inpDev in bringConnectBackList:
        subprocess.run(["pw-link", "-L", outDev, inpDev])
    microSteam.stop_stream()
    microSteam.close()
    outputStream.stop_stream()
    outputStream.close()
    app.terminate()
    WORKING_APP = False
    sys.exit(0)

signal.signal(signal.SIGTERM, handleKill)
signal.signal(signal.SIGINT, handleKill)

while WORKING_APP:
    data = microSteam.read(CHUNK, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    audio /= 32768.0  # normalize to -1..1
    shifted = pyrb.pitch_shift(audio, RATE, n_steps=SHIFT_VOICE_PITCH)
    shifted = np.clip(shifted * 32768, -32768, 32767).astype(np.int16).tobytes()
    outputStream.write(shifted)
