import os
import sys
import socket
from PythonFileLibrary.FileReader import *

# Read from configuration file first
configFile = FileReader('config')


def GetSetting(fileReader: FileReader, setting: str):
    fileReader.ResetCursor()

    for line in configFile:
        line = line.strip()
        if setting in line:
            fileReader.MoveCursorDown()
            line = fileReader.GetCurrentLine().strip()
            return line

    return None


def getPrivateIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.10.0.0", 1))
        return s.getsockname()[0]
    except:
        pass

    return None


localIP = getPrivateIP()
remoteIP = GetSetting(configFile,   '# Remote Public IP Address')
port = GetSetting(configFile,       '# Port')
protocol = GetSetting(configFile,   '# Protocol (UDP / TCP)')
height = GetSetting(configFile,     '# Height')
width = GetSetting(configFile,      '# Width')
FPS = GetSetting(configFile,        '# FPS')
bitrate = GetSetting(configFile,    '# Bitrate')
quality = GetSetting(configFile,    '# Quality (10 - 40)')

UDPcommand = "raspivid -n -t 0 -w {0} -h {1} -qp {6} -fps {2} --flush -b {3} -o - | gst-launch-1.0 -e -vvvv fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host={4} port={5}"
TCPcommand = "raspivid -n -t 0 -w {0} -h {1} -qp {6} -fps {2} --flush -b {3} -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host={4} port={5}"

UDPcommand_libcamera = "libcamera-raw --width {0} --height {1} --framerate {2} --bitrate {3} --quality {6} --timeout 0 --verbose --nopreview - | gst-launch-1.0 -e -vvvv fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host={4} port={5}"
TCPcommand_libcamera = "libcamera-raw --width {0} --height {1} --framerate {2} --bitrate {3} --quality {6} --timeout 0 --verbose --nopreview - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host={4} port={5}"

if protocol == "TCP":
    print("Trying to send through TCP pipe...")
    command = TCPcommand_libcamera.format(
        width, height, FPS, bitrate, localIP, port, quality)
    print(command)
    os.system(command)
elif protocol == "UDP":
    print("Trying to send through UDP pipe...")
    command = UDPcommand_libcamera.format(
        width, height, FPS, bitrate, remoteIP, port, quality)
    print(command)
    os.system(command)
