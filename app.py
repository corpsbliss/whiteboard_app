from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
import paramiko

app = Flask(__name__)

NOTES_DIR = 'notes'
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)


SFTP_HOST = '65.0.180.235'
SFTP_PORT = 22
SFTP_USER = 'sftpuser'
PRIVATE_KEY_PATH = '/whiteboard_app/key/sftpuser_key'
REMOTE_DIR = 'upload'  


def upload_to_sftp(local_path, remote_filename):
    try:
        key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, pkey=key)

        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_path = f'{REMOTE_DIR}/{remote_filename}'
        sftp.put(local_path, remote_path)

        sftp.close()
        transport.close()
        print(f"Uploaded {local_path} to {remote_path} on SFTP server.")
    except Exception as e:
        print(f"[SFTP Upload Failed] {e}")


def delete_from_sftp(remote_filename):
    try:
        key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, pkey=key)

        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_path = f'{REMOTE_DIR}/{remote_filename}'
        sftp.remove(remote_path)

        sftp.close()
        transport.close()
        print(f"Deleted {remote_path} from SFTP server.")
    except Exception as e:
        print(f"[SFTP Delete Failed] {e}")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt'
            filepath = os.path.join(NOTES_DIR, filename)
            with open(filepath, 'w') as f:
                f.write(user_input)

            # Upload to SFTP server
            upload_to_sftp(filepath, filename)

        return redirect(url_for('index'))

    files = sorted(os.listdir(NOTES_DIR), reverse=True)
    return render_template('index.html', files=files, content=None, selected=None)


@app.route('/view/<filename>')
def view_file(filename):
    filepath = os.path.join(NOTES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        files = sorted(os.listdir(NOTES_DIR), reverse=True)
        return render_template('index.html', files=files, content=content, selected=filename)
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(NOTES_DIR, filename, as_attachment=True)


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(NOTES_DIR, filename)

    
    if os.path.exists(filepath):
        os.remove(filepath)

    
    delete_from_sftp(filename)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

