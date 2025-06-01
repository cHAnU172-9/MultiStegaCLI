# MultiStegaCLI

**MultiStegaCLI** is a powerful Linux-based command-line tool that allows users to securely embed and extract hidden data from various types of digital media including **images**, **audio**, **video**, and **text files** using multiple steganographic techniques. Designed with modularity and extensibility in mind, this tool is ideal for cybersecurity professionals, digital forensics experts, and privacy-conscious users.

---

## 🚀 Features

- 🔐 **AES Encryption** for added payload confidentiality
- 🖼️ **LSB (Least Significant Bit)** for image and text steganography
- 🎞️ **DCT (Discrete Cosine Transform)** for JPEG images
- 🎵 **Phase Encoding** for audio signals
- 📹 **Adaptive Steganography** for video files
- 📂 Support for a wide range of file formats
- 🧩 Format detection & payload size validation
- 💻 Simple and efficient CLI interface
- 🔧 Modular architecture for easy extension

---

## 🔧 Technologies Used

- Python 3.x
- OpenCV (`cv2`)
- NumPy
- FFmpeg / moviepy
- wave, pydub (for audio handling)
- cryptography (for AES)
- argparse (for CLI design)

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MultiStegaCLI.git
   cd MultiStegaCLI
