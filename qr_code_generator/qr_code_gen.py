import qrcode.image.svg

# Data to encode
data = "https://cmmc-kb.gnps2.org/structurepage/?inchikey=AUNGANRZJHBGPY-SCRDCRAPSA-N"
save_to = "cmmc-kb-riboflavin_2.svg"

factory = qrcode.image.svg.SvgImage

# Create QR code instance
qr = qrcode.QRCode(
    version=1,  # controls the size of the QR code
    error_correction=qrcode.constants.ERROR_CORRECT_M,  # error correction level
    box_size=10,  # size of each box in pixels
    border=4,  # thickness of the border (minimum is 4)
)

# Add data to the QR code
qr.add_data(data)
qr.make(fit=True)

# Create an SVG image from the QR code instance
img = qr.make_image(image_factory=factory)

# Save the SVG image to a file
img.save(save_to)
