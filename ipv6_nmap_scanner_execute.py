import csv
import codecs
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# File paths
csv_file_path = 'nmap_scan_table.csv'
output_file_path = 'nmap_commands.txt'

# Default interface (user can change this)
default_interface = input("Enter the default interface (e.g., eth1) [default: eth1]: ") or 'eth1'

# Limit the number of simultaneous commands to avoid overloading the system
MAX_CONCURRENT_SCANS = 3  # Adjust as needed

# Lists to store the parsed data
scan_ids = []
ecu_names = []
vlan_names = []
vlan_ids = []
source_ips = []
source_ports = []
destination_ips = []
destination_ports = []

# Read and parse the CSV file
with codecs.open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    
    for row in csv_reader:
        # Append data to respective lists
        scan_ids.append(row['Scan-ID'].strip())
        ecu_names.append(row['ECU_Name'].strip())
        vlan_names.append(row['VLAN_Name'].strip())
        vlan_ids.append(row['VLAN-ID'].strip())
        source_ips.append(row['Source-IP'].strip())
        source_ports.append(row['Source-Port'].strip())
        destination_ips.append(row['Destination-IP'].strip())
        destination_ports.append(row['Destination-Port'].strip())

# Prepare separate lists for Nmap scan commands
stealth_scan_commands = []
connected_scan_commands = []

def create_vlan_subinterface(interface, vlan_id, source_ip):
    """Check if a VLAN subinterface exists, create if it doesn't, and assign the source IP with a /64 subnet."""
    
    vlan_interface = f"{interface}.{vlan_id}"
    
    # Show the progress bar for subinterface creation and IP assignment
    with tqdm(total=3, desc=f"Configuring {vlan_interface}", unit="step") as progress_bar:
        
        # Check if the VLAN subinterface already exists
        result = subprocess.run(f"ip link show {vlan_interface}", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"VLAN subinterface {vlan_interface} already exists. Skipping creation.")
        else:
            try:
                # Create the VLAN subinterface if it doesn't exist
                subprocess.run(f"sudo ip link add link {interface} name {vlan_interface} type vlan id {vlan_id}", shell=True, check=True)
                # Bring the VLAN subinterface up
                subprocess.run(f"sudo ip link set dev {vlan_interface} up", shell=True, check=True)
                print(f"VLAN {vlan_id} interface {vlan_interface} created successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create VLAN subinterface {vlan_interface}: {e}")
                return  # Exit this step if the subinterface cannot be created

        # Update progress after checking/creating the interface
        progress_bar.update(1)
        
        # Assign the source IP with /64 subnet to the VLAN subinterface
        try:
            subprocess.run(f"sudo ip addr add {source_ip}/64 dev {vlan_interface}", shell=True, check=True)
            print(f"IP address {source_ip}/64 assigned to {vlan_interface}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to assign IP address {source_ip}/64 to {vlan_interface}: {e}")
            return

        # Update progress after assigning IP address
        progress_bar.update(1)
        
        # Show current IPv6 addresses after configuration
        show_ipv6_addresses()
        
        # Update progress bar after displaying IPs
        progress_bar.update(1)

def show_ipv6_addresses():
    """Shows all IPv6 addresses and their interfaces on the system."""
    result = subprocess.run("ip -6 addr show", shell=True, capture_output=True, text=True)
    ipv6_info = result.stdout
    print("\nCurrent IPv6 addresses and interfaces:")
    print(ipv6_info)
    return ipv6_info

def prompt_user_confirmation():
    """Prompts user for confirmation to proceed."""
    response = input("Do you accept this configuration? (Y/n): ").strip().lower()
    return response == 'y'

def clear_vlan_configuration(interface, vlan_id):
    """Clears the VLAN subinterface configuration."""
    vlan_interface = f"{interface}.{vlan_id}"
    try:
        subprocess.run(f"sudo ip link delete {vlan_interface}", shell=True, check=True)
        print(f"Cleared configuration for VLAN interface {vlan_interface}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clear configuration for {vlan_interface}: {e}")

# Create VLAN subinterfaces and set source IPs
for scan_id, ecu_name, vlan_id, src_ip, src_port, dest_ip, dest_port in zip(scan_ids, ecu_names, vlan_ids, source_ips, source_ports, destination_ips, destination_ports):
    if vlan_id != '1':  # Skip VLAN 1
        create_vlan_subinterface(default_interface, vlan_id, src_ip)
    
    port_option = f'-p {dest_port}' if dest_port else '-p-'
    base_filename = f"{ecu_name}_VLAN.{vlan_id}"
    stealth_output_xml = f"{base_filename}_sS_{scan_id}.xml"
    stealth_output_standard = f"{base_filename}_sS_{scan_id}.nmap"
    connected_output_xml = f"{base_filename}_sT_{scan_id}.xml"
    connected_output_standard = f"{base_filename}_sT_{scan_id}.nmap"
    
    # Nmap commands with interface specification (-e)
    interface_option = f"-e {default_interface}" if vlan_id == '1' else f"-e {default_interface}.{vlan_id}"

    # Construct the -g option if src_port is provided
    src_port_option = f"-g {src_port}" if src_port else ""

    stealth_command = (
        f'nmap -6 -sS -n -Pn -T4 --reason {src_port_option} -S {src_ip} {port_option} {dest_ip} {interface_option} '
        f'-oX {stealth_output_xml} -oN {stealth_output_standard}'
    )
    connected_command = (
        f'nmap -6 -sT -n -Pn --reason {src_port_option} -S {src_ip} {port_option} {dest_ip} {interface_option} '
        f'-oX {connected_output_xml} -oN {connected_output_standard}'
    )
    
    stealth_scan_commands.append(stealth_command)
    connected_scan_commands.append(connected_command)
    
# Show all IPv6 addresses and interfaces, then prompt for user confirmation
ipv6_info = show_ipv6_addresses()

if not prompt_user_confirmation():
    print("User did not accept the configuration. Clearing subinterface configurations...")
    for vlan_id in vlan_ids:
        if vlan_id != '1':  # Clear configuration for non-VLAN 1
            clear_vlan_configuration(default_interface, vlan_id)
    exit(0)  # Exit the script if the user does not confirm

print("User accepted the configuration. Proceeding with Nmap scans...")

# Write all the Nmap commands to a text file (optional)
with open(output_file_path, mode='w') as file:
    file.write("Stealth Scan Commands:\n")
    for command in stealth_scan_commands:
        file.write(command + "\n")
    
    file.write("\nConnected Scan Commands:\n")
    for command in connected_scan_commands:
        file.write(command + "\n")

# Function to execute a command in a separate screen session
def execute_command(command, session_name):
    """Executes the given command in a new detached screen session."""
    # Construct the screen command to run the Nmap scan in a new detached session
    screen_command = f'screen -dmS {session_name} bash -c "{command}; exec bash"'
    
    # Print and show the progress of each command execution
    print(f"Starting scan in screen session: {session_name}")
    
    process = subprocess.Popen(screen_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()  # Wait for the command to be submitted
    return command

# Execute commands in parallel with a limit on concurrent tasks
def run_commands(commands, prefix="scan"):
    """Executes the given commands in parallel and tracks progress."""
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SCANS) as executor:
        future_to_command = {}
        
        # Set up the progress bar for Nmap scanning progress
        with tqdm(total=len(commands), desc=f"Nmap Scans in {prefix} Sessions", unit="scan") as progress_bar:
            # Generate unique session names for each command
            for i, cmd in enumerate(commands):
                session_name = f"{prefix}_session_{i + 1}"
                future = executor.submit(execute_command, cmd, session_name)
                future_to_command[future] = cmd
            
            for future in as_completed(future_to_command):
                command = future_to_command[future]
                try:
                    future.result()
                    progress_bar.update(1)
                except Exception as exc:
                    print(f"Command {command} generated an exception: {exc}")
            
            progress_bar.close()

# Execute Stealth and Connected scans separately (with scheduling)
print(f"Executing {len(stealth_scan_commands)} stealth scan commands...")
run_commands(stealth_scan_commands, prefix="stealth")


time.sleep(2)  # Short pause between command sets

print(f"Executing {len(connected_scan_commands)} connected scan commands...")
run_commands(connected_scan_commands, prefix="connected")

print("All scans completed.")
