import qrcode, time

data = input("Welcome to IndianCoder3 QR Code generator! Please enter the text/URL you wnat to convert to a URL:    ")
filename = ("QR_" + data) + ".png"

qr = qrcode.QRCode(
    version=1,  # Controls the size of the QR code (1 to 40)
    error_correction=qrcode.constants.ERROR_CORRECT_L, # Error correction level (L, M, Q, H)
    box_size=10, # Size of each box (pixel) in the QR code
    border=4, # Thickness of the border around the QR code
)
qr.add_data(data)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save(filename)

print("Output saved as " + filename)
print("Quitting in 20 seconds")
time.sleep(20)