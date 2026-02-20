## NetworkManager Wi-Fi Configuration (iPhone.nmconnection)

⚠️ This file replaces the traditional `bootfs` Wi-Fi setup method.<br>
⚠️ The `bootfs` method is often unreliable and non-persistent.<br>
⚠️ The `.nmconnection` file provides a stable and persistent configuration managed directly by NetworkManager.<br>
⚠️ It enables automatic connection on boot and maintains wireless settings across reboots.<br><br>

### Compatibility Notice<br>
This configuration only supports **WPA-PSK (WPA Personal)** networks such as mobile phone hotspots or home Wi-Fi routers.<br>
It does **not** support enterprise or organization networks using WPA-Enterprise (e.g., 802.1X, EAP).<br><br>

## 🔧 RPI Network Configuration Guide<br>

### 1️⃣ Modify Required Fields<br>
Edit the following inside the file:<br>
`psk=<Password>`<br>
`ssid=<your actual wireless SSID>`<br>
`id=<your actual wireless SSID>`<br>

📛 Replace `<Password>` with your Wi-Fi password.<br>
📛 Ensure both `ssid` and `id` match your exact wireless network name.<br><br>

### 2️⃣ Rename the File<br>
After editing, rename:<br>
`iPhone.nmconnection`<br>
to match your wireless SSID.<br>

Example:<br>
If your SSID is `HomeWiFi`, rename the file to:<br>
`HomeWiFi.nmconnection`<br>

### 3️⃣ Apply the Configuration<br>
Copy the file to:<br>
`/etc/NetworkManager/system-connections/`<br>

Set proper permissions:<br>
`sudo chmod 600 <filename>.nmconnection`<br>

Restart NetworkManager:<br>
`sudo systemctl restart NetworkManager`<br>

-

## 🔧 Firmware Boot Configuration
To configure the system booting settings, edit the config file on your Raspberry Pi: 
`sudo vim /boot/firmware/config.txt`

### Configuration Steps
You can find an example configuration in this repo: [config.txt]
(https://github.com/KannaKobayashiDragon/RaspberryPiConfigurationExample/blob/main/config.txt)

* **Update Hardware Sections:** Delete the `[cm4]` and `[cm5]` sections. Replace them with the `[all]` section provided in the repository to ensure the settings apply to all models.

```ini
[all]
enable_uart=1
dtoverlay=dwc2,dr_mode=peripheral
Headless Mode: If you are running the Pi without a monitor (headless), go to the bottom of the file and comment out the HDMI output lines. This saves about 20-30mA of power and improves Wi-Fi stability.

# Disable HDMI output completely to save power and improve Wi-Fi stability
hdmi_ignore_hotplug=1
hdmi_blanking=1
```

