# Network Interface Management Tool

This Python script provides a command-line tool for managing network interfaces and VLAN subinterfaces on a Linux system. It allows you to display available network interfaces, create VLAN subinterfaces, change IPv6 addresses on VLAN interfaces, and delete VLAN subinterfaces.

## Features

- **Show Interfaces:** List all available network interfaces along with their IPv6 addresses.
- **Create VLAN Subinterface:** Create a VLAN subinterface on a base network interface and assign an IPv6 address to it.
- **Change VLAN IPv6 Address:** Modify the IPv6 address of an existing VLAN subinterface, with an option to delete the old address.
- **Delete VLAN Subinterface:** Remove a VLAN subinterface from the system.

## Prerequisites

- Python 3.x
- Linux-based system
- Required utilities installed (`ip`, `subprocess`)

## How to Use

1. **Clone or Download the Script:**
   ```bash
   git clone https://github.com/VATASec/Authomotive_Ethernet.git
   cd network-interface-tool
2. Run the Script:
   ```bash
   python3 network_interface_tool.py

3. Choose an Action:
   When prompted, select an action by entering the corresponding number:

    - 1: Show interfaces
    - 2: Add VLAN interface and set IPv6
    - 3: Change VLAN IPv6 address
    - 4: Delete VLAN subinterface
    - 5: Exit

Follow Prompts:

    The script will guide you through the process of managing interfaces. You will be asked to provide necessary inputs, such as the base interface name, VLAN ID, or IPv6 addresses.
