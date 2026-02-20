RaspberryPiConfigurationExample is a configuration repository designed specifically for the Raspberry Pi Zero 2 W.
-
🔧 Modify the following fields inside the file:<br>
`psk=<Password>`<br>
`ssid=<your actual wireless SSID>`<br>
`id=<your actual wireless SSID>`<br>

📛 Replace `<Password>` with your Wi-Fi password. <br>
Ensure both ssid and id match your exact wireless network name.<br>

📛 Rename the file<br>
After editing, rename iPhone.nmconnection to match your wireless SSID.<br>
Example: If your SSID is HomeWiFi, rename the file to HomeWiFi.nmconnection.<br>

📂 Apply the configuration<br>
Copy the file to /etc/NetworkManager/system-connections/<br>

📂 Set proper permissions:<br>
`sudo chmod 600 <filename>.nmconnection`<br>

📂 Restart NetworkManager to apply changes:<br>
`sudo systemctl restart NetworkManager`<br>
