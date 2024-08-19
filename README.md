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
   git clone https://github.com/your-repo/network-interface-tool.git
   cd network-interface-tool
