# RaspberryPiConfigurationExample
RaspberryPiConfigurationExample is a configuration repository designed specifically for the Raspberry Pi Zero 2 W.<br>

🔧 Modify the following fields inside the file:
psk=<Password>
ssid=<your actual wireless SSID>
id=<your actual wireless SSID>

Replace <Password> with your Wi-Fi password.
Ensure both ssid and id match your exact wireless network name.

📛 Rename the file
After editing, rename iPhone.nmconnection to match your wireless SSID.
Example: If your SSID is HomeWiFi, rename the file to HomeWiFi.nmconnection.

📂 Apply the configuration
Copy the file to /etc/NetworkManager/system-connections/

Set proper permissions:
sudo chmod 600 <filename>.nmconnection

Restart NetworkManager to apply changes:
sudo systemctl restart NetworkManager<br>
