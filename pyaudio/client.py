import numpy as np
import wave
import pyaudio
import socket
import threading
import time

streamstop = False

def SoundStreamClient(server_host, server_port):
    SERVER_HOST = server_host
    SERVER_PORT = int(server_port)

    global streamstop
    audio = pyaudio.PyAudio()

    # オーディオプロパティ
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 4096
    INPUT_DEVICE_INDEX = 1

    # マイクの入力ストリーム生成
    mic_stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input_device_index=INPUT_DEVICE_INDEX,
                            input=True,
                            frames_per_buffer=CHUNK)

    # サーバに接続
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))

        # サーバにオーディオプロパティを送信
        sock.send("{},{},{},{}".format(
            FORMAT, CHANNELS, RATE, CHUNK).encode('utf-8'))

        print("Start")
        # メインループ
        while True:
            if streamstop == False:
                mic_data = mic_stream.read(CHUNK)
                decoded_mic_data = np.frombuffer(mic_data, np.int16).copy()
                decoded_mic_data.resize(CHANNELS * CHUNK, refcheck=False)
                send_data = (decoded_mic_data).astype(np.int16).tobytes()

                # サーバに音データを送信
                sock.send(send_data)

            else:
                break

    # 終了処理
    mic_stream.stop_stream()
    mic_stream.close()
    audio.terminate()

def main_func():
    global streamstop
    mss_client = threading.Thread(target=SoundStreamClient, args=("localhost", 12345,))
    mss_client.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("stop")
            streamstop = True
            break

    mss_client.join()

if __name__ == '__main__':
    main_func()
