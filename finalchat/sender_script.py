import os
from tqdm import tqdm
import socket
import threading
import rsa
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def pad(text):
    pad_size = 16 - (len(text) % 16)
    return text + bytes([pad_size] * pad_size)


def unpad(text):
    pad_size = text[-1]
    return text[:-pad_size]


def encrypt_message(message, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    message = pad(message.encode())
    ciphertext = cipher.encrypt(message)
    return ciphertext


def encrypt_data(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = pad(data)
    ciphertext = cipher.encrypt(data)
    return ciphertext


def decrypt_message(encrypted_message, key, iv):
    ciphertext = encrypted_message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return unpad(plaintext).decode()


def decrypt_data(encrypted_message, key, iv):
    ciphertext = encrypted_message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return unpad(plaintext)


def sending_messages(c, key, iv):

    # Reading public RSA key of sender host for encryption
    with open("reciever_public.pem", "rb") as f:
        sender_public_key = rsa.PublicKey.load_pkcs1(f.read())

    while True:
        message = input("")
        if (message.startswith("File:")):
            file_path = message.split(":")[1].strip()
            base_file_name = os.path.basename(file_path)

            # Sending the file name
            file_name = "@File_name:" + base_file_name
            AES_encrypted_message = encrypt_message(file_name, key, iv)
            RSA_encrypted_message = rsa.encrypt(
                AES_encrypted_message, sender_public_key)
            c.sendall(RSA_encrypted_message)

            # Sending file size
            file_size = os.path.getsize(file_path)
            c.sendall(str(file_size).encode())

            # Sending the actual file data
            with open(file_path, 'rb') as file:
                with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        AES_encrypted_data = encrypt_data(data, key, iv)
                        c.sendall(AES_encrypted_data)
                        pbar.update(len(data))

        else:
            AES_encrypted_message = encrypt_message(message, key, iv)
            RSA_encrypted_message = rsa.encrypt(
                AES_encrypted_message, public_key)
            c.sendall(RSA_encrypted_message)
            print("You: " + message)


def recieving_file(c, file_name, key, iv):
    file_size = int(c.recv(1024).decode())
    # file_size_bytes = c.recv(1024)
    # print(file_size_bytes)
    # file_size = int.from_bytes(file_size_bytes, byteorder='big', signed=False)
    file_name = "sender_recieved/"+file_name
    received_data = b''
    with open(file_name, 'wb') as file:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            while len(received_data) < file_size:
                encrypted_data = c.recv(1024)
                decrypted_data = decrypt_data(
                    encrypted_data, key, iv)
                received_data += decrypted_data
                pbar.update(len(encrypted_data))
        file.write(received_data)


def recieving_messages(c, key, iv):

    with open("sender_private.pem", "rb") as f:
        reciever_private_key = rsa.PrivateKey.load_pkcs1(f.read())

    while True:
        encrypted_message = c.recv(1024)
        if (len(encrypted_message) != 0):
            AES_encrypted_message = rsa.decrypt(
                encrypted_message, reciever_private_key)
            decrypted_message = decrypt_message(AES_encrypted_message, key, iv)
            if (decrypted_message.startswith("@File_name:")):
                recieving_file(c, decrypted_message[11:], key, iv)
            else:
                print("Partner: " + decrypted_message)


if __name__ == "__main__":
    host = '10.81.58.32'
    port = 9999

    with open("reciever_public.pem", "rb") as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())

    with open("sender_private.pem", "rb") as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Generating sender AES key
    Sender_AES_key = get_random_bytes(16)
    Sender_AES_iv = get_random_bytes(16)

    key_to_send = Sender_AES_key+Sender_AES_iv
    encrypted_message = rsa.encrypt(key_to_send, public_key)
    s.sendall(encrypted_message)

    # Recieving Reciever AES keys
    encrypted_message = s.recv(1024)
    decrypted_message = rsa.decrypt(encrypted_message, private_key)
    Reciever_AES_key = decrypted_message[:16]
    Reciever_AES_iv = decrypted_message[16:32]

    print("Successfully recieved and decrypted Reciever AES key\n\n")

    print("Directly type the message to send the text.")
    print("To send data type File:path to file")
    print("all the recieved files are stored in sender_recieved folder\n")

    threading.Thread(target=sending_messages, args=(
        s, Sender_AES_key, Sender_AES_iv)).start()
    threading.Thread(target=recieving_messages, args=(
        s, Reciever_AES_key, Reciever_AES_iv)).start()
