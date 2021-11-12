import pyaudio
import socket
import threading
import wave

class SoundStreamServer(threading.Thread):
    def __init__(self, server_host, server_port):
        threading.Thread.__init__(self)
        self.SERVER_HOST = server_host
        self.SERVER_PORT = int(server_port)

    def run(self):
        audio = pyaudio.PyAudio()
        # ファイル出力先
        # filepath = "sample.wav"

        # サーバーソケット生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind((self.SERVER_HOST, self.SERVER_PORT))
            server_sock.listen(1)

            # クライアントと接続
            client_sock, _ = server_sock.accept()
            with client_sock:
                # クライアントからオーディオプロパティを受信
                settings_list = client_sock.recv(256).decode('utf-8').split(",")
                FORMAT = int(settings_list[0])
                CHANNELS = int(settings_list[1])
                RATE = int(settings_list[2])
                CHUNK = int(settings_list[3])

                # オーディオ出力ストリーム生成 
                stream = audio.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    output=True,
                                    frames_per_buffer=CHUNK)

                # ファイル出力定義
                # wave_f = wave.open(filepath, 'wb')
                # wave_f.setnchannels(1)
                # wave_f.setsampwidth(2)
                # wave_f.setframerate(16000)

                # メインループ
                while True:
                    # クライアントから音データを受信
                    data = client_sock.recv(CHUNK)
                    # ファイル出力処理
                    # wave_f.writeframes((data))

                    # 切断処理
                    if not data:
                        break

                    # オーディオ出力ストリームにデータ書き込み
                    stream.write(data)

        # 終了処理
        stream.stop_stream()
        stream.close()

        audio.terminate()

if __name__ == '__main__':
    mss_server = SoundStreamServer("localhost", 12345)
    mss_server.start()
    mss_server.join()