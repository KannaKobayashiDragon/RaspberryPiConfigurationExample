# RaspberryPiConfigurationExample

RaspberryPiConfigurationExample is a configuration repository designed specifically for the Raspberry Pi Zero 2 W.<br>

## NetworkManager Wi-Fi Configuration (iPhone.nmconnection)

⚠️ This file replaces the traditional `bootfs` Wi-Fi setup method.<br>
⚠️ The `bootfs` method is often unreliable and non-persistent.<br>
⚠️ The `.nmconnection` file provides a stable and persistent configuration managed directly by NetworkManager.<br>
⚠️ It enables automatic connection on boot and maintains wireless settings across reboots.<br><br>

### Compatibility Notice<br>
This configuration only supports **WPA-PSK (WPA Personal)** networks such as mobile phone hotspots or home Wi-Fi routers.<br>
It does **not** support enterprise or organization networks using WPA-Enterprise (e.g., 802.1X, EAP).<br><br>

## 🔧 Configuration Guide<br>

### 1️⃣ Modify Required Fields<br>
Edit the following inside the file:<br>
`psk=<Password>`<br>
`ssid=<your actual wireless SSID>`<br>
`id=<your actual wireless SSID>`<br><br>

📛 Replace `<Password>` with your Wi-Fi password.<br>
📛 Ensure both `ssid` and `id` match your exact wireless network name.<br><br>

### 2️⃣ Rename the File<br>
After editing, rename:<br>
`iPhone.nmconnection`<br>
to match your wireless SSID.<br><br>

Example:<br>
If your SSID is `HomeWiFi`, rename the file to:<br>
`HomeWiFi.nmconnection`<br><br>

### 3️⃣ Apply the Configuration<br>
Copy the file to:<br>
`/etc/NetworkManager/system-connections/`<br><br>

Set proper permissions:<br>
`sudo chmod 600 <filename>.nmconnection`<br><br>

Restart NetworkManager:<br>
`sudo systemctl restart NetworkManager`<br>
