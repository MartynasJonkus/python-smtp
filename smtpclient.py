import socket
import ssl
import base64


class SMTPClient:
    def __init__(self, server, port, username, password):
        self.last_response = None
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server, self.port))
        print("AFTER SOCKET CONNECT:\n")
        self.receive_response()

        print("AFTER EHLO:\n")
        self.send_command('EHLO example.com')
        if 'STARTTLS' in self.last_response:
            print("AFTER STARTTLS:\n")
            self.send_command('STARTTLS')
            self.socket = ssl.wrap_socket(self.socket, ssl_version=ssl.PROTOCOL_TLS)
        else:
            raise RuntimeError("STARTTLS is not supported by the SMTP server")

    def receive_response(self):
        response = self.socket.recv(1024).decode()
        print(response)
        self.last_response = response

    def send_command(self, command):
        self.socket.send((command + '\r\n').encode())
        self.receive_response()

    def send_command_no_response(self, command):
        self.socket.send((command + '\r\n').encode())

    def login(self):
        print("AFTER RE-SEND EHLO:\n")
        self.send_command('EHLO example.com')
        print("AFTER AUTH LOGIN:\n")
        self.send_command('AUTH LOGIN')
        print("AFTER USERNAME:\n")
        self.send_command(base64.b64encode(self.username.encode()).decode())
        print("AFTER PASSWORD:\n")
        self.send_command(base64.b64encode(self.password.encode()).decode())

    def send_mail(self, sender, recipients, subject, body, attachment_filename=None):
        print(f"AFTER MAIL FROM:<{sender}>:")
        self.send_command(f'MAIL FROM:<{sender}>')
        for recipient in recipients:
            print(f"AFTER RCPT TO:<{recipient}>:")
            self.send_command(f'RCPT TO:<{recipient}> ')
        print("AFTER DATA:")
        self.send_command('DATA')

        boundary = "===============7330845974216740156=="
        mime_message = f"""\
From: {sender}
To: {', '.join(recipients)}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit

{body}

--{boundary}
"""

        if attachment_filename:
            with open(attachment_filename, "rb") as attachment_file:
                attachment_content = base64.b64encode(attachment_file.read()).decode("utf-8")
            mime_message += f"""\
Content-Type: application/octet-stream; name="{attachment_filename}"
Content-Disposition: attachment; filename="{attachment_filename}"
Content-Transfer-Encoding: base64

{attachment_content}

--{boundary}
"""

        print(mime_message)
        self.send_command_no_response(mime_message)
        print("AFTER dot sign:")
        self.send_command('.')
        print("AFTER QUIT:")
        self.send_command('QUIT')

    def close(self):
        self.socket.close()


def xor_encrypt(text, key):
    encrypted_text = ""
    key_length = len(key)
    for i in range(len(text)):
        encrypted_text += chr(ord(text[i]) ^ ord(key[i % key_length]))
    encoded_base = base64.b64encode(encrypted_text.encode()).decode()
    return encoded_base


def xor_decrypt(encrypted_text, key):
	text = base64.b64decode(encrypted_text).decode()
	original_message = ""
	key_length = len(key)
	for i in range(len(text)):
		original_message += chr(ord(text[i]) ^ ord(key[i % key_length]))
	return original_message


if __name__ == "__main__":
    server = 'smtp.gmail.com'
    port = 587
    username = 'example@gmail.com'
    password = 'password'

    client = SMTPClient(server, port, username, password)
    client.connect()
    client.login()

    sender = 'example@gmail.com'
    recipients = ['receiver1@gmail.com', 'receiver2@gmail.com']
    subject = 'An encrypted message'
    body = '''This may be an encrypted message if the user uses the encrypt function'''
    attachment_filename = 'text.txt'
    key = '''Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere'''
    encrypted_message = xor_encrypt(body, key)

    client.send_mail(sender, recipients, subject, encrypted_message)
    client.close()
