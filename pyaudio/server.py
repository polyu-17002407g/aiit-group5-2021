import pyaudio
import socket
import threading
import wave
import asyncio
import sys
import boto3

from queue import Queue
from datetime import date, datetime
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

queue = Queue()
no_data = False

class SoundStreamServer(threading.Thread):
    def __init__(self, server_host, server_port):
        threading.Thread.__init__(self)
        self.SERVER_HOST = server_host
        self.SERVER_PORT = int(server_port)

    def run(self):
        audio = pyaudio.PyAudio()
        global queue, no_data

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
                # stream = audio.open(format=FORMAT,
                #                     channels=CHANNELS,
                #                     rate=RATE,
                #                     output=True,
                #                     frames_per_buffer=CHUNK)

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
                        no_data = True
                        break

                    # オーディオ出力ストリームにデータ書き込み
                    # stream.write(data)
                    # ストリームをQueueに保存
                    queue.put(data)
                    

        # 終了処理
        # stream.stop_stream()
        # stream.close()
        queue.put(None)
        audio.terminate()


class ParseTranscribeResultAndUploadToS3(TranscriptResultStreamHandler):
    def __init__(self, TranscriptResultStream, bucket_name, threshold=3):
        super().__init__(TranscriptResultStream)
        self.S3_CLIENT = boto3.client('s3')
        self.BUCKET_NAME = bucket_name
        self.THRESHOLD = threshold
        self.wite_partial = 0
        self.date_time = None

    # S3にアップロード
    def upload_to_s3(self, text):
        key = "origin/record_{}.txt".format(self.date_time)
        self.S3_CLIENT.put_object(Body=text, Bucket=self.BUCKET_NAME, Key=key)

    # 文字起こしの結果を抽出
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        num_chars_printed = 0
        interim_flush_counter = 0
        for result in results:
            if not self.date_time:
                self.date_time = datetime.now().strftime("%Y%m%d%H%M%S%f")
            transcript = result.alternatives[0].transcript
            overwrite_chars = " " * (num_chars_printed - len(transcript))
            if result.is_partial:
                # 文字起こしの途中
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()
                interim_flush_counter += 1

                num_chars_printed = len(transcript)
                self.wite_partial += 1
                if self.wite_partial < self.THRESHOLD:
                    pass
                else:
                    self.wite_partial = 0
                    self.upload_to_s3(transcript)
            else:
                # 文字起こしの結果が決定
                text = transcript + overwrite_chars
                self.upload_to_s3(text)
                self.date_time = None
                self.wite_partial = 0
                # print(text)
                num_chars_printed = 0


class StreamingClientWrapper:
    def __init__(self, region, lang, sample_rate, bucket_name):
        self.REGION = region
        self.LANG = lang
        self.SAMPLE_RATE = sample_rate
        self.BUCKET_NAME = bucket_name

    async def start_listen(self):
        # AWSクライアント生成 (リージョン)
        speech_client = TranscribeStreamingClient(region=self.REGION)
        # AWS文字起こしの準備
        stream = await speech_client.start_stream_transcription(
            language_code=self.LANG,
            media_sample_rate_hz=self.SAMPLE_RATE,
            media_encoding="pcm",
        )
        # 文字起こし
        async def write_chunks(stream):
            global queue, no_data
            while not queue.empty() or not no_data:
                await stream.input_stream.send_audio_event(audio_chunk=queue.get())
            await stream.input_stream.end_stream()

        handler = ParseTranscribeResultAndUploadToS3(stream.output_stream, bucket_name=self.BUCKET_NAME)
        await asyncio.gather(write_chunks(stream), handler.handle_events())
        

if __name__ == '__main__':
    mss_server = SoundStreamServer("localhost", 12345)
    wrapper = StreamingClientWrapper("<region>", "en-US", 16000, "<bucket_name>")

    loop = asyncio.get_event_loop()
    mss_server.start()
    loop.run_until_complete(wrapper.start_listen())
    mss_server.join()
    loop.close()