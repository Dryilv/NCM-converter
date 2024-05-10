# ncm_converter.py
import binascii
import struct
import base64
import json
import os
from Crypto.Cipher import AES

class NCMConverter:
    def __init__(self):
        self.core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
        self.meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
        self.unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]

    def dump(self, file_path, output_dir):
        with open(file_path, 'rb') as f:
            header = f.read(8)
            assert binascii.b2a_hex(header) == b'4354454e4644414d'
            f.seek(2, 1)
            key_length = struct.unpack('<I', f.read(4))[0]
            key_data = bytearray(f.read(key_length))
            for i in range(len(key_data)):
                key_data[i] ^= 0x64
            key_data = self.unpad(AES.new(self.core_key, AES.MODE_ECB).decrypt(bytes(key_data)))[17:]
            key_box = self.create_key_box(key_data)

            meta_length = struct.unpack('<I', f.read(4))[0]
            meta_data = bytearray(f.read(meta_length))
            for i in range(len(meta_data)):
                meta_data[i] ^= 0x63
            meta_data = base64.b64decode(bytes(meta_data)[22:])
            meta_data = json.loads(self.unpad(AES.new(self.meta_key, AES.MODE_ECB).decrypt(meta_data)).decode('utf-8')[6:])

            f.read(4)  # Skip CRC32
            f.seek(5, 1)  # Skip 5 unknown bytes
            image_size = struct.unpack('<I', f.read(4))[0]
            f.read(image_size)  # Skip image data

            file_name = f"{meta_data['musicName']}.{meta_data['format']}"
            output_path = os.path.join(output_dir, file_name)
            self.decrypt_music_data(f, key_box, output_path)

        return output_path


    def create_key_box(self, key_data):
        key_length = len(key_data)
        key_box = bytearray(range(256))
        c = 0
        last_byte = 0
        key_offset = 0
        for i in range(256):
            swap = key_box[i]
            c = (swap + last_byte + key_data[key_offset]) & 0xff
            key_offset = (key_offset + 1) % key_length
            key_box[i] = key_box[c]
            key_box[c] = swap
            last_byte = c
        return key_box

    def decrypt_music_data(self, f, key_box, output_path):
        with open(output_path, 'wb') as m:
            while chunk := bytearray(f.read(0x8000)):
                for i in range(len(chunk)):
                    j = (i + 1) & 0xff
                    chunk[i] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
                m.write(chunk)
