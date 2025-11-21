import streamlit as st
from PIL import Image
import numpy as np
import io
import os

# ==========================
# IMAGE PROCESSING FUNCTIONS
# ==========================

def load_image_file(file):
    img = Image.open(file)
    mode = img.mode
    arr = np.array(img)
    return arr, mode

def save_image_to_bytes(arr, mode):
    img = Image.fromarray(arr.astype(np.uint8), mode=mode)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def shuffle_pixels(arr, key, encrypt=True):
    shape = arr.shape
    flat = arr.reshape(-1, shape[-1]) if arr.ndim == 3 else arr.reshape(-1)
    n = flat.shape[0]

    rng = np.random.RandomState(abs(hash(str(key))) % (2**32))
    perm = rng.permutation(n)

    if encrypt:
        shuffled = flat[perm]
        result = shuffled.reshape(shape)
    else:
        inv = np.empty_like(perm)
        inv[perm] = np.arange(n)
        unshuffled = flat[inv]
        result = unshuffled.reshape(shape)

    return result

def add_value(arr, value, encrypt=True):
    if not encrypt:
        value = (-value) % 256
    return (arr.astype(np.int32) + value) % 256

def xor_value(arr, value):
    return arr.astype(np.uint8) ^ (value & 0xFF)


# ==========================
# STREAMLIT APP
# ==========================

st.title("🔐 Image Encryption Tool - Streamlit Version")
st.write("Upload an image and apply **Shuffle**, **Add Value**, or **XOR Encryption**.")

uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded:
    arr, mode = load_image_file(uploaded)

    st.image(arr, caption="Original Image", use_column_width=True)
    st.write("---")

    operation = st.selectbox(
        "Choose an Operation",
        ["Shuffle Pixels", "Add Value (mod 256)", "XOR Value"]
    )

    decrypt_mode = st.checkbox("Decrypt instead of Encrypt")

    # Parameters based on operation
    if operation == "Shuffle Pixels":
        key = st.text_input("Enter shuffle key (string or number)", "mykey")
    elif operation == "Add Value (mod 256)":
        key = st.number_input("Enter value (0–255)", 0, 255, 50)
    elif operation == "XOR Value":
        key = st.number_input("Enter XOR byte (0–255)", 0, 255, 77)

    if st.button("Process Image"):
        st.write("🔄 Processing...")

        if operation == "Shuffle Pixels":
            out = shuffle_pixels(arr, key, encrypt=not decrypt_mode)

        elif operation == "Add Value (mod 256)":
            out = add_value(arr, key, encrypt=not decrypt_mode).astype(np.uint8)

        elif operation == "XOR Value":
            out = xor_value(arr, key)

        st.image(out, caption="Processed Image", use_column_width=True)

        # Convert to downloadable PNG
        result_bytes = save_image_to_bytes(out, mode)

        st.download_button(
            label="📥 Download Encrypted Image",
            data=result_bytes,
            file_name="encrypted_output.png",
            mime="image/png"
        )
