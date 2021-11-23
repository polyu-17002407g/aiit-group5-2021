from flask import Flask, request
import os
import client
import time

app = Flask(__name__)
stream_start_file = "streamingstart.bat"
zoom_start_file = "zoomstart.bat"
zoom_stop_file = "zoomstop.bat"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/transtart')
def transtartCall():
    confno = request.args.get('confno')
    confpwd = request.args.get('confpwd')

    zoom_start_bat = zoom_start_file + " " + confno + " " + confpwd
    os.system(zoom_start_bat)
    time.sleep(5)
    os.system(stream_start_file)
    client.start_client()
    return "Transxxx Service Start!"


@app.route('/transtop')
def transtopCall():
    client.stop_client()
    os.system(zoom_stop_file)
    return "Transxxx Service Stop!"


@app.route('/shutdown')
# サーバーのシャットダウン
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == "__main__":
    # WebAPIの呼び出し
    app.run(host='0.0.0.0', port=9999, debug=True)
