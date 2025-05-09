import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image
import base64
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class QRSettings:
    """Dataclass to store QR code settings"""
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    box_size: int = 10
    border: int = 4
    error_correction: str = "H"


class QRCodeGenerator:
    """Class to handle QR code generation"""
    
    def __init__(self, settings: Optional[QRSettings] = None):
        self.settings = settings or QRSettings()
    
    def generate(self, data: str) -> Tuple[Image.Image, bytes]:
        """
        Generate a QR code with the provided data and current settings
        Returns both the PIL Image and the bytes representation
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Map string error correction to qrcode constants
        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        error_correction = error_levels.get(self.settings.error_correction, qrcode.constants.ERROR_CORRECT_H)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=self.settings.box_size,
            border=self.settings.border
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(
            fill_color=self.settings.fill_color, 
            back_color=self.settings.back_color
        )
        
        # Convert image to bytes for Streamlit
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        return img, img_bytes


def get_image_download_link(img_bytes: bytes, filename: str, text: str) -> str:
    """Generate a download link for an image"""
    img_str = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{img_str}" download="{filename}">{text}</a>'
    return href


def main():
    # Page config
    st.set_page_config(
        page_title="QR Code Generator",
        page_icon="📱"
    )
    
    # Header
    st.title("📱 QR Code Generator")
    st.markdown("Generate QR codes for links, text, and more.")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_type = st.radio(
            "Input Type",
            ["URL", "Text", "Email", "Phone", "WiFi"],
            horizontal=True
        )
        
        data = ""
        if input_type == "URL":
            data = st.text_input("Enter URL", placeholder="https://example.com")
            
        elif input_type == "Text":
            data = st.text_area("Enter Text", placeholder="Your text here")
            
        elif input_type == "Email":
            email = st.text_input("Email Address", placeholder="example@example.com")
            subject = st.text_input("Subject (Optional)", placeholder="Hello")
            body = st.text_input("Body (Optional)", placeholder="Message content")
            
            if email:
                data = f"mailto:{email}"
                if subject:
                    data += f"?subject={subject}"
                    if body:
                        data += f"&body={body}"
                elif body:
                    data += f"?body={body}"
            
        elif input_type == "Phone":
            phone = st.text_input("Phone Number", placeholder="+1234567890")
            if phone:
                data = f"tel:{phone}"
                
        elif input_type == "WiFi":
            ssid = st.text_input("Network Name (SSID)")
            password = st.text_input("Password", type="password")
            encryption = st.selectbox("Encryption", ["WPA/WPA2", "WEP", "None"])
            
            if ssid:
                encryption_map = {"WPA/WPA2": "WPA", "WEP": "WEP", "None": "nopass"}
                data = f"WIFI:S:{ssid};T:{encryption_map[encryption]};"
                if password and encryption != "None":
                    data += f"P:{password};"
                data += ";"
    
    with col2:
        st.subheader("QR Settings")
        fill_color = st.color_picker("Fill Color", "#000000")
        back_color = st.color_picker("Background Color", "#FFFFFF")
        box_size = st.slider("Box Size", 1, 20, 10)
        border = st.slider("Border", 0, 10, 4)
        error_correction = st.selectbox(
            "Error Correction",
            options=["L", "M", "Q", "H"],
            index=3,
            help="L: 7%, M: 15%, Q: 25%, H: 30% recovery"
        )
        
        settings = QRSettings(
            fill_color=fill_color,
            back_color=back_color,
            box_size=box_size,
            border=border,
            error_correction=error_correction
        )
    
    # Generate button
    if st.button("✨ Generate QR Code", type="primary", use_container_width=True):
        if data:
            try:
                # Generate QR code
                qr_generator = QRCodeGenerator(settings)
                _, img_bytes = qr_generator.generate(data)
                
                # Display QR code
                st.subheader("Your QR Code 📲")
                st.image(img_bytes, use_container_width=True)
                
                # Provide download link
                download_link = get_image_download_link(img_bytes, "qrcode.png", "📥 Download QR Code")
                st.markdown(download_link, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating QR code: {str(e)}")
        else:
            st.warning("⚠️ Please enter some data to generate a QR code")


if __name__ == "__main__":
    main()