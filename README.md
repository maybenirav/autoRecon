# auto-recon & vuln finder 🕵️‍♂️

hey! i built this python framework to automate the boring parts of my CTFs and penetration testing labs. instead of manually running nmap, dirb, and searchsploit one by one, i wanted a script that just handles the heavy lifting for me. 

it's split into two main engines: one for mapping out the target (recon), and one for finding actual exploits (vuln). 

## what it actually does
* **recon mode (`-r`):** maps the footprint. it runs a whois lookup, hunts subdomains with assetfinder, checks open ports with nmap, grabs the tech stack with whatweb, and fuzzes directories with dirb.
* **vuln mode (`-v`):** hunts for weaknesses. does a deep service version scan, runs offline exploit-db checks via searchsploit, and audits the web server using nikto.
* **all-in-one (`-a`):** runs the entire pipeline back-to-back and dumps everything into one clean, timestamped text file.

## stuff you need installed
i built this on kali linux, so you probably already have most of this. to make sure you have all the required tools, just run this quick command in your terminal:

```bash
sudo apt update
sudo apt install nmap whois assetfinder whatweb dirb nikto exploitdb -y