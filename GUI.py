import streamlit as st
from PIL import Image
import qrcode
from io import BytesIO
import re
import os


def make_qr(data: str, fill_color: str = "black", back_color: str = "white", box_size: int = 10, border: int = 4) -> Image.Image:
	"""Create a PIL Image containing the QR code for `data`.

	Returns:
		PIL.Image.Image: The generated QR code image.
	"""
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=box_size,
		border=border,
	)
	qr.add_data(data)
	qr.make(fit=True)
	img = qr.make_image(fill_color=fill_color, back_color=back_color)
	return img


def sanitize_filename(s: str) -> str:
	# replace characters that are invalid in filenames on Windows
	s = re.sub(r'[\\/*?:"<>|]', '_', s)
	s = s.strip()
	return s or "QR"


def is_likely_url(s: str) -> bool:
	"""Return True if the string looks like a URL or domain."""
	s = s.strip()
	if not s:
		return False
	# quick checks: starts with scheme or looks like domain
	if re.match(r'https?://', s, re.IGNORECASE):
		return True
	# domain-like: contains a dot and no spaces
	if re.match(r'^[\w.-]+\.[a-zA-Z]{2,}(/.*)?$', s):
		return True
	return False


def normalize_url(s: str) -> str:
	"""Ensure the URL has a scheme. If missing, add https:// by default."""
	s = s.strip()
	if not s:
		return s
	if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', s):
		return s
	return 'https://' + s


def main() -> None:
	st.set_page_config(page_title="QR Code Generator", layout="centered")
	st.title("QR Code Generator")
	st.write("Enter text or a URL and press Generate to create a QR code.")

	data = st.text_area("Text / URL", value="", height=160)

	col1, col2, col3 = st.columns([1, 1, 1])
	with col1:
		box_size = st.slider("Box size", min_value=1, max_value=20, value=10)
	with col2:
		border = st.slider("Border", min_value=1, max_value=10, value=4)
	with col3:
		save_to_disk = st.checkbox("Save to disk")

	c1, c2 = st.columns(2)
	with c1:
		fill_color = st.color_picker("Fill color", "#000000")
	with c2:
		back_color = st.color_picker("Background color", "#ffffff")

	filename_input = st.text_input("Filename (optional, without extension)")

	likely_url = is_likely_url(data)
	treat_as_url = False
	if likely_url:
		treat_as_url = st.checkbox("Treat input as URL", value=True)

	if st.button("Generate QR"):
		if not data.strip():
			st.warning("Please enter some text or a URL to generate a QR code.")
		else:
			payload = data
			if treat_as_url:
				payload = normalize_url(data)
				st.markdown(f"**Detected URL:** [{payload}]({payload})")

			img = make_qr(payload, fill_color=fill_color, back_color=back_color, box_size=box_size, border=border)
			buf = BytesIO()
			img.save(buf, format="PNG")
			buf.seek(0)

			st.image(buf, caption="Generated QR code", use_column_width=False)

			# prepare filename
			if filename_input.strip():
				fname = sanitize_filename(filename_input)
			else:
				# derive a short filename from the data
				short = sanitize_filename(data)[:50]
				fname = f"QR_{short}"
			full_fname = f"{fname}.png"

			# download button expects bytes
			st.download_button("Download PNG", data=buf.getvalue(), file_name=full_fname, mime="image/png")

			if save_to_disk:
				save_path = os.path.join(os.getcwd(), full_fname)
				# write from the same buffer (rewind first)
				buf.seek(0)
				with open(save_path, "wb") as f:
					f.write(buf.getvalue())
				st.success(f"Saved to {save_path}")
	else:
		st.info("Waiting for input. Type text or a URL and click 'Generate QR'.")


if __name__ == "__main__":
	main()

