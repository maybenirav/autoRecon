import sys
import subprocess
import argparse
import os
from datetime import datetime

# terminal color definitions
g = '\033[92m'   # green
r = '\033[91m'   # red
c = '\033[96m'   # cyan
y = '\033[93m'   # yellow
reset = '\033[0m'

def print_banner():
    banner = f"""{c}
     ____  ____  ___  __  __ _ 
    (  _ \(  __)/ __)/  \(  ( \\
     )   / ) _)( (__(  O ))    /
    (__\_)(____)\___)\__/\_)__)
    
    {g}:: dual-engine recon & vulnerability framework ::{reset}
    """
    print(banner)

def parse_arguments():
    parser = argparse.ArgumentParser(description="dual-engine automated reconnaissance & vulnerability scanner")
    
    parser.add_argument("-t", "--target", required=True, help="target ip address or domain to scan")
    parser.add_argument("-r", "--recon", action="store_true", help="run pure reconnaissance phase (osint, ports, tech, fuzzing)")
    parser.add_argument("-v", "--vuln", action="store_true", help="run vulnerability & exploit check phase (searchsploit, nikto)")
    parser.add_argument("-a", "--all", action="store_true", help="run both recon and vulnerability phases (default)")
    
    args = parser.parse_args()
    
    args.clean_target = args.target.replace("http://", "").replace("https://", "").strip("/")
    if not args.clean_target:
        print(f"{r}[-] error: target cannot be empty.{reset}")
        sys.exit(1)
        
    # default to running both phases if neither -r nor -v is explicitly selected
    if not args.recon and not args.vuln:
        args.all = True
        
    return args

def create_report_file(target):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{target}_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("MASTER SECURITY ASSESSMENT REPORT\n")
            file.write(f"target: {target}\n")
            file.write(f"timestamp: {timestamp}\n")
            file.write("=" * 60 + "\n\n")
        return filename
    except Exception as e:
        print(f"\n{r}[-] error creating report file: {e}{reset}")
        sys.exit(1)

def run_tool(command_list, report_file, tool_name, section_header):
    print(f"\n{c}[*] launching {tool_name}...{reset}")
    
    try:
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            errors="replace"
        )
        
        with open(report_file, "a", encoding="utf-8") as file:
            file.write(f"=== {section_header} ===\n\n")
            if result.stdout.strip():
                file.write(result.stdout)
            else:
                file.write("[-] no direct output returned.\n")
                
            if result.stderr.strip():
                file.write("\n[errors / warnings]:\n" + result.stderr)
            file.write("\n" + "=" * 60 + "\n\n")
            
        print(f"{g}[+] {tool_name} completed!{reset}")
        
    except FileNotFoundError:
        print(f"{r}[-] error: {tool_name} is not installed on this system path.{reset}")
        with open(report_file, "a", encoding="utf-8") as file:
            file.write(f"=== {section_header} ===\n\n[-] tool not installed on host.\n\n" + "=" * 60 + "\n\n")
    except Exception as e:
        print(f"{r}[-] unexpected error running {tool_name}: {e}{reset}")

def run_recon_phase(target, target_url, report_file):
    print(f"\n{g}>>> STARTING PHASE 1: RECONNAISSANCE <<<{reset}")
    run_tool(['whois', target], report_file, "whois osint", "WHOIS RECORD")
    run_tool(['assetfinder', '--subs-only', target], report_file, "assetfinder (subdomains)", "SUBDOMAIN ENUMERATION")
    run_tool(['nmap', '-T4', '--top-ports', '1000', target], report_file, "nmap port discovery", "NMAP OPEN PORTS")
    run_tool(['whatweb', target_url], report_file, "whatweb fingerprinting", "WEB APPLICATION STACK")
    run_tool(['dirb', target_url, '-S'], report_file, "dirb directory fuzzer", "DIRB DISCOVERED PATHS")

def run_vuln_phase(target, target_url, report_file):
    print(f"\n{y}>>> STARTING PHASE 2: VULNERABILITY & EXPLOIT SEARCH <<<{reset}")
    nmap_xml = f"nmap_temp_{target}.xml"
    
    # 1. version scan to generate exploit mapping data
    print(f"\n{c}[*] running deep service version scan for exploit detection...{reset}")
    nmap_args = ['nmap', '-T4', '--top-ports', '1000', '-sV', '-sC', '-oX', nmap_xml, target]
    run_tool(nmap_args, report_file, "nmap service & version scan", "NMAP SERVICE DETECTION")
    
    # 2. searchsploit offline lookup
    if os.path.exists(nmap_xml):
        print(f"\n{y}[*] hunting known public exploits with searchsploit...{reset}")
        run_tool(['searchsploit', '--nmap', nmap_xml], report_file, "searchsploit exploit hunter", "SEARCHSPLOIT EXPLOIT MATCHES")
        try:
            os.remove(nmap_xml)
        except OSError:
            pass
    else:
        print(f"{r}[-] nmap xml not generated, skipping searchsploit.{reset}")
        
    # 3. nikto web vulnerability scanner
    run_tool(['nikto', '-h', target_url, '-Tuning', '10', '-maxtime', '1m'], report_file, "nikto web audit", "NIKTO WEB VULNERABILITY AUDIT")

if __name__ == "__main__":
    try:
        print_banner()
        args = parse_arguments()
        
        target = args.clean_target
        report_file = create_report_file(target)
        target_url = f"http://{target}"
        
        print(f"{g}[+] master report initialized: {report_file}{reset}")
        
        # execute selected modules
        if args.all or args.recon:
            run_recon_phase(target, target_url, report_file)
            
        if args.all or args.vuln:
            run_vuln_phase(target, target_url, report_file)
            
        print(f"\n{g}======================================================{reset}")
        print(f"{g}[+] scan finished successfully!{reset}")
        print(f"{g}[+] full results compiled in: {c}{report_file}{reset}")
        print(f"{g}======================================================{reset}")
        
    except KeyboardInterrupt:
        print(f"\n\n{r}[!] process interrupted by user. exiting cleanly...{reset}")
        sys.exit(0)
