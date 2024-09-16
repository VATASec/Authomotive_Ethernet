import csv
import codecs

# File path to your CSV file
csv_file_path = 'nmap_scan_table.csv'
output_file_path = 'nmap_commands.txt'  # File path for the output text file

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
    
    # Iterate through each row in the CSV
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

for scan_id, ecu_name, vlan_id, src_ip, src_port, dest_ip, dest_port in zip(scan_ids, ecu_names, vlan_ids, source_ips, source_ports, destination_ips, destination_ports):
    # Determine the port option based on whether the destination port is empty
    if dest_port:
        port_option = f'-p {dest_port}'
    else:
        port_option = '-p-'
    
    # Construct the source port option only if src_port is not empty
    src_port_option = f'-g {src_port}' if src_port else ''

    # Construct the output file names
    base_filename = f"{ecu_name}_VLAN.{vlan_id}"
    stealth_output_xml = f"{base_filename}_sS_{scan_id}.xml"
    stealth_output_standard = f"{base_filename}_sS_{scan_id}.nmap"
    connected_output_xml = f"{base_filename}_sT_{scan_id}.xml"
    connected_output_standard = f"{base_filename}_sT_{scan_id}.nmap"
    
    # Construct a Stealth Scan command with output options
    stealth_command = (
        f'nmap -6 -sS -n -Pn -T4 --reason {src_port_option} -S {src_ip} {port_option} {dest_ip} '
        f'-oX {stealth_output_xml} -oN {stealth_output_standard}'
    )
    
    # Construct a Connected Scan command with output options
    connected_command = (
        f'nmap -6 -sT -n -Pn --reason {src_port_option} -S {src_ip} {port_option} {dest_ip} '
        f'-oX {connected_output_xml} -oN {connected_output_standard}'
    )
    
    # Append commands to their respective lists
    stealth_scan_commands.append(stealth_command)
    connected_scan_commands.append(connected_command)

# Write all the Nmap commands to a single text file
with open(output_file_path, mode='w') as file:
    file.write("Stealth Scan Commands:\n")
    for command in stealth_scan_commands:
        file.write(command + "\n")
    
    file.write("\nConnected Scan Commands:\n")
    for command in connected_scan_commands:
        file.write(command + "\n")

print(f"Nmap commands have been written to {output_file_path}")
