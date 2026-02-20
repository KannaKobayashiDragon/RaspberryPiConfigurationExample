## NetworkManager Wi-Fi Configuration (iPhone.nmconnection)

⚠️ This file replaces the traditional `bootfs` Wi-Fi setup method.<br>
⚠️ The `bootfs` method is often unreliable and non-persistent.<br>
⚠️ The `.nmconnection` file provides a stable and persistent configuration managed directly by NetworkManager.<br>
⚠️ It enables automatic connection on boot and maintains wireless settings across reboots.<br>

### Compatibility Notice
This configuration only supports **WPA-PSK (WPA Personal)** networks such as mobile phone hotspots or home Wi-Fi routers.
It does **not** support enterprise or organization networks using WPA-Enterprise (e.g., 802.1X, EAP).

## 🔧 RPI Network Configuration Guide

### 1️⃣ Modify Required Fields
Edit the following inside the file:
* `psk=<Password>`
* `ssid=<your actual wireless SSID>`
* `id=<your actual wireless SSID>`

📛 Replace `<Password>` with your Wi-Fi password.<br>
📛 Ensure both `ssid` and `id` match your exact wireless network name.

### 2️⃣ Rename the File
After editing, rename `iPhone.nmconnection` to match your wireless SSID.

Example:
If your SSID is `HomeWiFi`, rename the file to: `HomeWiFi.nmconnection`

### 3️⃣ Apply the Configuration
Copy the file to the system directory, set the required permissions, and restart the service:

```bash
# Copy to the system connections folder
sudo cp <filename>.nmconnection /etc/NetworkManager/system-connections/

# Set proper permissions (Required for security)
sudo chmod 600 /etc/NetworkManager/system-connections/<filename>.nmconnection

# Restart NetworkManager to apply changes
sudo systemctl restart NetworkManager
```

---

## 🔧 Firmware Boot Configuration
To configure the system booting settings, edit the config file on your Raspberry Pi: <br>
`sudo vim /boot/firmware/config.txt`

### Configuration Steps
You can find an example configuration in this repo: [config.txt](https://github.com/KannaKobayashiDragon/RaspberryPiConfigurationExample/blob/main/config.txt)

* **Update Hardware Sections:** Delete the `[cm4]` and `[cm5]` sections.<br>
Replace them with the `[all]` section provided in the repository to ensure the settings apply to all models

```ini
[all]
enable_uart=1
dtoverlay=dwc2,dr_mode=peripheral
```

* **Headless Mode:** If you are running the Pi without a monitor (headless), go to the bottom of the file and comment out the HDMI output lines.<br>
This saves about 20-30mA of power and improves Wi-Fi stability.

```ini
# Enable DRM VC4 V3D driver
# dtoverlay=vc4-kms-v3d
# max_framebuffers=2
# Uncomment this section if using non Headless-Mode on Raspberry Pi. 
# - Reduce 20-30 mA

# Disable HDMI output completely to save power and improve Wi-Fi stability
hdmi_ignore_hotplug=1
hdmi_blanking=1
```

---

## 🔌 USB Gadget Mode Configuration
To configure the USB gadget mode modules, edit the following configuration file:<br>
`sudo vim /etc/modules-load.d/usb-gadget.conf`

### Configuration Steps
You can find an example configuration in this repo: [usb-gadget.config](https://github.com/KannaKobayashiDragon/RaspberryPiConfigurationExample/blob/main/usb-gadget.config)

### Validation
Reboot the Raspberry Pi and verify that the modules have loaded correctly:

```bash
sudo reboot
```

After the system reboots and you reconnect, run:
```bash
lsmod | grep -E 'dwc2|libcomposite'
```

**Expected Output:**
```text
libcomposite           65536  10 usb_f_hid
dwc2                  176128  0
roles                  16384  1 dwc2
```

---

## ⌨️ HID Setup Scripting
To set up the HID gadget script, create and edit the following file:<br>
`sudo vim /usr/bin/HID_Gadget`

### Script Configuration
You can find an example script in this repo: [HID_GADGET](https://github.com/KannaKobayashiDragon/RaspberryPiConfigurationExample/blob/main/HID_GADGET)

Make the script executable:<br>
```bash
sudo chmod +x /usr/bin/HID_Gadget
```

### Register as a Daemon Service
Create and configure the systemd service to run the HID gadget script on boot:<br>
`sudo vim /etc/systemd/system/raspkey-usbhid.service`

### Reboot and Validate
Reboot the Raspberry Pi using an **OTG Cable connected to the Data Port**:<br>
```bash
sudo reboot
```

After rebooting, check if the HID device was created successfully:<br>
```bash
ls -l /dev/hidg0
```

### 🧪 HID Testing
If `/dev/hidg0` exists, test the keyboard output. The following commands will type the letter '**a**' on the connected workstation.<br>

```bash
# Press 'a'
echo -ne "\x00\x00\x04\x00\x00\x00\x00\x00" | sudo tee /dev/hidg0 > /dev/null

# Release the key
echo -ne "\x00\x00\x00\x00\x00\x00\x00\x00" | sudo tee /dev/hidg0 > /dev/null
```
