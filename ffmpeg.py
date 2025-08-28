import subprocess
import time
import signal
import sys

STREAM_NAME = "VoiceChanger"
RATE = 48000
CHANNELS = 2

MIC_DEVICE = ""#"alsa_input.pci-0000_09_00.4.analog-stereo"
HEAD_PHONE_DEVICE = ""#"alsa_output.pci-0000_09_00.4.analog-stereo"
APP_VOICE_CHANGER = "Lavf60.16.100"
APP_DISCORD_NAME = "WEBRTC VoiceEngine"

WORKING_PROCESS = True

F = 2 ** (3/12)  # pitch factor for -4 semitones

af = ""
af += f"asetrate={RATE}*{F},aresample={RATE},atempo={1/F},"

result = subprocess.run(["pw-link", "-l"], capture_output=True, text=True).stdout.splitlines()
for line in result:
    if not line.startswith(' '):
        if "alsa_input" in line:
            MIC_DEVICE = line[:-len(":captureAAA")]
        elif "alsa_output" in line:
            HEAD_PHONE_DEVICE = line[:-len(":playbackAAA")]

ff = subprocess.Popen(
    [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-probesize", "32",
        "-analyzeduration", "0",
        "-thread_queue_size", "64",
        "-f", "pulse", "-i", MIC_DEVICE,
        "-ar", str(RATE),
        "-ac", f"{CHANNELS}",
        "-probesize", "32",
        "-analyzeduration", "0",
        "-thread_queue_size", "64",
        "-af", af,
        "-f", "pulse", "-device", MIC_DEVICE, STREAM_NAME
    ],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    bufsize=0
)

def createTupleDevice(device, type):
    return (f"{device}:{type}_FL", f"{device}:{type}_FR")

microProvider = createTupleDevice(MIC_DEVICE, "capture")
headPhoneDevice = createTupleDevice(HEAD_PHONE_DEVICE, "playback")
changeVoiceOutput = createTupleDevice(APP_VOICE_CHANGER, "output")
discordDevice = createTupleDevice(APP_DISCORD_NAME, "input")

disconnectionPairFL = list(zip(microProvider, discordDevice))+list(zip(changeVoiceOutput, headPhoneDevice))

connectionList = list(zip(changeVoiceOutput, discordDevice))

bringConnectBackList = list(zip(microProvider, discordDevice))

time.sleep(1)
for outPut, inPut in disconnectionPairFL:
    subprocess.run([ "pw-link", "-d", outPut, inPut ])

time.sleep(1)
for outPut, inPut in connectionList:
    subprocess.run([ "pw-link", "-L", outPut, inPut ])

def handleKill(signum, frame):
    global run
    print("Handle KILl HANDLEED")
    for outDev, inpDev in bringConnectBackList:
        subprocess.run(["pw-link", "-L", outDev, inpDev])
    ff.kill()
    run = False
    sys.exit(0)

signal.signal(signal.SIGTERM, handleKill)
signal.signal(signal.SIGINT, handleKill)

while WORKING_PROCESS:
    time.sleep(0.5)
if ff.stderr != None:
    print(ff.stderr.readlines())
