
import cv2
import struct
import bitstring
import numpy  as np
import zigzag as zz
import sys
import data_embedding as stego
import image_preparation   as img
from crypt import AESCipher
out_img = sys.argv[1]
out_file = sys.argv[2]
password = sys.argv[3]

#out_img = sys.argv[1]
stego_image     = cv2.imread(out_img, flags=cv2.IMREAD_COLOR)
stego_image_f32 = np.float32(stego_image)
stego_image_YCC = img.YCC_Image(cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb))

# FORWARD DCT STAGE
dct_blocks = [cv2.dct(block) for block in stego_image_YCC.channels[0]]  # Only care about Luminance layer

# QUANTIZATION STAGE
dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]

# Sort DCT coefficients by frequency
sorted_coefficients = [zz.zigzag(block) for block in dct_quants]

# DATA EXTRACTION STAGE
recovered_data = stego.extract_encoded_data_from_DCT(sorted_coefficients)
recovered_data.pos = 0

# Determine length of secret message
data_len = int(recovered_data.read('uint:32') / 8)

# Extract secret message from DCT coefficients
extracted_data = bytes()
for _ in range(data_len): extracted_data += struct.pack('>B', recovered_data.read('uint:8'))

cipher = AESCipher(password)
data_dec = cipher.decrypt(extracted_data)

# Write decrypted data
out_f = open(out_file, "wb")
out_f.write(data_dec)
out_f.close()
