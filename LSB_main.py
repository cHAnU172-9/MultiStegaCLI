import time
import psutil
import os
import sys
import struct
import numpy
import matplotlib.pyplot as plt

from PIL import Image

from crypt import AESCipher

# Decompose a binary file into an array of bits
def decompose(data):
    v = []
    
    # Pack file len in 4 bytes
    fSize = len(data)
    bytes = [b for b in struct.pack("i", fSize)]
    
    bytes += [b for b in data]

    for b in bytes:
        for i in range(7, -1, -1):
            v.append((b >> i) & 0x1)

    return v

# Assemble an array of bits into a binary file
def assemble(v):    
    byte_data = bytearray()  # Use bytearray for efficiency

    length = len(v)
    print(f"[DEBUG] Bitstream length: {length}")  # Debugging

    for idx in range(0, length // 8):  # Use // for integer division
        byte = 0
        for i in range(8):
            if (idx * 8 + i < length):
                byte = (byte << 1) + v[idx * 8 + i]                
        byte_data.append(byte)  # Efficient appending

        # Debug every 10000 bytes to avoid excessive logs
        if idx % 10000 == 0:
            pass #print(f"[DEBUG] Processed {idx} bytes...")

    payload_size = struct.unpack("i", byte_data[:4])[0]
    print(f"[DEBUG] Extracted payload size: {payload_size}")

    return byte_data[4: payload_size + 4]


# Set the i-th bit of v to x
def set_bit(n, i, x):
    mask = 1 << i
    n &= ~mask
    if x:
        n |= mask
    return n

# Embed payload file into LSB bits of an image
def embed(imgFile, payload, password):
    # Process source image
    img = Image.open(imgFile)
    (width, height) = img.size
    conv = img.convert("RGBA").getdata()
    print("Input image size:", width, height, "pixels.")
    max_size = width * height * 3.0 / 8 / 1024  # max payload size
    print("[*] Usable payload size:", max_size, "KB.")

    f = open(payload, "rb")
    data = f.read()
    f.close()
    print("[+] Payload size: {:.3f} KB".format(len(data)/1024.0))
    
    # Encrypt
    cipher = AESCipher(password)
    data_enc = cipher.encrypt(data)

    # Process data from payload file
    v = decompose(data_enc)
    
    # Add until multiple of 3
    while len(v) % 3:
        v.append(0)

    payload_size = len(v) / 8 / 1024.0
    print("[+] Encrypted payload size: {:.3f} KB".format(payload_size))
    if payload_size > max_size - 4:
        print("[-] Cannot embed. File too large")
        sys.exit()
    
    # Create output image
    steg_img = Image.new('RGBA', (width, height))
    data_img = steg_img.getdata()

    idx = 0

    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            if idx < len(v):
                r = set_bit(r, 0, v[idx])
                g = set_bit(g, 0, v[idx+1])
                b = set_bit(b, 0, v[idx+2])
            data_img.putpixel((w, h), (r, g, b, a))
            idx += 3
    
    steg_img.save("out_stego.png", "PNG")
    
    print("[+] {} embedded successfully!".format(payload))

# Extract data embedded into LSB of the input file
def extract(in_file, out_file, password):
    # Process source image
    img = Image.open(in_file)
    (width, height) = img.size
    conv = img.convert("RGBA").getdata()
    print("[+] Image size: {}x{} pixels.".format(width, height))

    # Extract LSBs
    v = []
    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            v.append(r & 1)
            v.append(g & 1)
            v.append(b & 1)
    
    data_out = assemble(v)

    # Decrypt
    cipher = AESCipher(password)
    data_dec = cipher.decrypt(data_out)

    # Write decrypted data
    out_f = open(out_file, "wb")
    out_f.write(data_dec)
    out_f.close()
    
    print("[+] Written extracted data to {}.".format(out_file))

# Statistical analysis of an image to detect LSB steganography
def analyse(in_file):
    BS = 100  # Block size 
    img = Image.open(in_file)
    (width, height) = img.size
    print("[+] Image size: {}x{} pixels.".format(width, height))
    conv = img.convert("RGBA").getdata()

    # Extract LSBs
    vr = []  # Red LSBs
    vg = []  # Green LSBs
    vb = []  # Blue LSBs
    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            vr.append(r & 1)
            vg.append(g & 1)
            vb.append(b & 1)

    # Average colours' LSB per each block
    avgR = []
    avgG = []
    avgB = []
    for i in range(0, len(vr), BS):
        avgR.append(numpy.mean(vr[i:i + BS]))
        avgG.append(numpy.mean(vg[i:i + BS]))
        avgB.append(numpy.mean(vb[i:i + BS]))

    # Nice plot 
    numBlocks = len(avgR)
    blocks = list(range(0, numBlocks))
    plt.axis([0, len(avgR), 0, 1])
    plt.ylabel('Average LSB per block')
    plt.xlabel('Block number')
    plt.plot(blocks, avgB, 'bo')
    plt.show()

# Usage function
def usage(progName):
    print("MultiStegaCLI - A Command line tool for Universal file type steganography.\n")
    print("Usage:")
    print("  {} hide <img_file> <payload_file> <password>".format(progName))
    print("  {} extract <stego_file> <out_file> <password>".format(progName))
    #print("  {} analyse <stego_file>".format(progName))
    sys.exit()
    
if __name__ == "__main__":
    process = psutil.Process(os.getpid())
    if len(sys.argv) < 3:
        usage(sys.argv[0])
    
    if sys.argv[1] == "hide":   	
        start_mem = process.memory_info().rss / 1024 
        embed(sys.argv[2], sys.argv[3], sys.argv[4])
        end_mem = process.memory_info().rss / 1024 
        print(f"💾 Memory Used: {end_mem - start_mem:.2f} KB")
        print(f"💻 CPU Usage: {process.cpu_percent(interval=1.0)}%")
    elif sys.argv[1] == "extract":
        est=time.time()
        extract(sys.argv[2], sys.argv[3], sys.argv[4])
        eet=time.time()
        print("extracting time: ",eet-est)
    elif sys.argv[1] == "analyse":
        analyse(sys.argv[2])
    else:
        print("[-] Invalid operation specified")

