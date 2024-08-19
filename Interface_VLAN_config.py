import subprocess
import re

def show_interfaces():
    """Get available network interfaces along with their IP addresses."""
    try:
        interfaces = {}
        # Execute the command to list network interfaces and their IP addresses
        output = subprocess.check_output("ip -o addr show", shell=True).decode('utf-8')
        # Use regular expression to extract interface names and their IP addresses
        # Adjusted regex to include VLAN interfaces like 'eth1.5'
        print("Available network interfaces and their IP addresses:")
        for line in output.splitlines():
            match = re.match(r'\d+: ([\w\d\.\-]+)    inet6 (\S+)', line)
            if match:
                interface, ip_address = match.groups()
                print(f"{interface} - IP Address: {ip_address}")
                
    except subprocess.CalledProcessError as e:
        print(f"Failed to get network interfaces: {e}")
     

def create_vlan_subinterface():
    """Create a VLAN subinterface and set its IPv6 address."""
    interface = input("Enter the base interface name (e.g., eth1): ")
    vlan_id = input("Enter the VLAN ID: ")
    ipv6_address = input("Enter the IP address to set (e.g., fd53:7cb8:383:3::x/64): ")
    try:
        subprocess.check_call(f"ip link add link {interface} name {interface}.{vlan_id} type vlan id {vlan_id}", shell=True)
        subprocess.check_call(f"ip link set dev {interface}.{vlan_id} up", shell=True)
        subprocess.check_call(f"ip -6 addr add {ipv6_address} dev {interface}.{vlan_id}", shell=True)
        print(f"VLAN subinterface {interface}.{vlan_id} created with IPv6 address {ipv6_address}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create VLAN subinterface: {e}")

def change_vlan_ip_address():
    """Change the IPv6 address of a VLAN interface, optionally deleting the old one."""
    interface = input("Enter the VLAN interface name (e.g., eth1.3): ")
    # Display current IPv6 addresses on the interface
    try:
        output = subprocess.check_output(f"ip -6 addr show {interface}", shell=True).decode('utf-8')
        print(f"Current IPv6 addresses on {interface}:")
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Failed to list IPv6 addresses: {e}")
        return

    delete_current_ip = input("Do you want to delete the current IP address? (Y/N): ").strip().upper()
    if delete_current_ip == "Y":
        ipv6_address_to_delete = input("Enter the IPv6 address to delete (e.g., fd53:7cb8:383:3::1/64): ")
        # Confirm that the user does not attempt to delete the link-local address
        if "fe80:" in ipv6_address_to_delete:
            print("Error: Attempted to delete the link-local address, which is not allowed.")
            return

        try:
            subprocess.check_call(f"ip -6 addr del {ipv6_address_to_delete} dev {interface}", shell=True)
            print(f"IPv6 address {ipv6_address_to_delete} deleted successfully from {interface}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to delete IPv6 address: {e}")
            # If deletion fails, return to avoid adding a new address unintentionally
            return

    new_ipv6_address = input("Enter the new IPv6 address to add (e.g., fd53:7cb8:383:4::1/64): ")
    try:
        subprocess.check_call(f"ip -6 addr add {new_ipv6_address} dev {interface}", shell=True)
        print(f"New IPv6 address {new_ipv6_address} added successfully to {interface}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add new IPv6 address: {e}")


def delete_vlan_subinterface():
    """Delete an IPv6 address from a specific interface."""
    interface = input("Enter the VLAN interface name (e.g., eth1.3): ")
    
    try:
        subprocess.check_call(f"ip link delete {interface}", shell=True)
        print(f"VLAN suninterface {interface} deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete VLAN subinterface: {e}")

def main():
    try:
        while True:
            print("\n1: Show interfaces")
            print("2: Add VLAN interface and set IPv6")
            print("3: Change VLAN IPv6 address")
            print("4: Delete VLAN subinterface")
            print("5: Exit\n")
            action = input("Select an action by number: ")
            
            if action == '1':
                show_interfaces()
            elif action == '2':
                create_vlan_subinterface()
            elif action == '3':
                change_vlan_ip_address()
            elif action == '4':
                delete_vlan_subinterface()
            elif action == '5':
                print("Exiting program.")
                break
            else:
                print("Invalid action selected.")
    except KeyboardInterrupt:
         # This block is executed when Ctrl+C is pressed
        print("\nExiting program due to user interruption.")

if __name__ == "__main__":
    main()