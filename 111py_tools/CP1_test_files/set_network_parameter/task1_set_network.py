import os
import time

Bandwidth = '10Mbps'
Delay = '10ms'
restore = False # Set to True to restore original settings after applying new ones

# Find the network interface name
IFNAME = os.popen("ip route show default | awk '/dev/ {print $5}'").read().strip()  
# Save the current network settings to a file (for debugging purposes)
os.system(f"sudo tcset {IFNAME} > {IFNAME}_tc_get{int(time.time())}.txt")
os.system(f"sudo tcset {IFNAME}")

# Set the network parameters using tcset
try:
    os.system(f"sudo tcset {IFNAME} --delay {Delay} --rate {Bandwidth} --overwrite")
    print(f"Setting network parameters: Delay={Delay}, Bandwidth={Bandwidth} on interface {IFNAME}")
except Exception as e:
    print(f"Error setting network parameters: {e}")
    
# Restore the original network settings
if restore:
    os.system(f"sudo tcdel {IFNAME}")