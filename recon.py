#!/usr/bin/env python3

#
# Attempt at a Python web reconaissance tool
#
#    This program can be redistributed and/or modified under the terms of the
#    GNU General Public License, either version 3 of the License, or (at your
#    option) any later version.
#
# TODO Configure tools with API tokens for subdomain enumeration
# TODO Provide intel output from Amass
# TODO Add DNS Takeover with Aquatone
# TODO Add more recon with wayback
# amass subdomain enumeration
#TODO wordlist?
#TODO Add rest of config settings from yml

#TODO amass IP intel on subdomains after comparing with asset finder

#TODO masscan results from amass intel make sure to cross reference domains from amass intel and assetfinder
# while adding domains from amass to list going to  gowitness or add domains from assetfinder to intel scan
# for mass scan while

import sys
import os
import argparse
import subprocess
import shutil
import yaml

def checkfile(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def prepare_dir(target):
    target_dir = os.path.abspath(os.path.join(target))
    os.makedirs(target_dir, exist_ok=True)
    screenshot_dir = os.path.abspath(os.path.join(target, 'gowitness'))
    os.makedirs(screenshot_dir, exist_ok=True)

def asset_finder(target, domains):
    print(f'[-] Running assetfinder on {target}')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/assetfinder.txt', 'a')
    for domain in domains:
        print(f"Running assetfinder on {domain}")
        result = subprocess.run(['assetfinder', '--subs-only', domain], stdout=subprocess.PIPE, text=True)
        output.write(result.stdout)
    output.close()

def amass(target, domains, dns):
    print(f'[-] amass on {target}')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/amass_output.txt', 'a')
    outfile = f'{path}/amass.txt'
    if len(domains) > 1:
        domain = ",".join(domains)
    else:
        domain = domains[0]
    if len(dns) > 1:
        nameservers = ",".join(dns)
    else:
        nameservers = dns[0]
    result = subprocess.run(['amass', 'enum', '-ip', '-r', nameservers, '-brute', '-d', domain, '-o', outfile], stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()
    subdomain_path = f'{path}/amass_subdomain.txt'
    ip_path = f'{path}/amass_ip.txt'
    subdomains = []
    ips = []
    with open(outfile) as file:
        lines = file.readlines()
        for line in lines:
            split_lines = line.split(' ')
            subdomains.append(split_lines[0])
            ips.extend(split_lines[1].strip('\n').split(','))
            ips = [ ip+'\n' for ip in ips]
        with open(subdomain_path, 'w') as file:
            file.writelines(sorted(set(subdomains)))
        with open(ip_path, 'w') as file:
            file.writelines(sorted(set(ips)))

def combine(target):
    print(f'[-] Combining on {target}')
    path = os.path.abspath(os.path.join(target))
    amass_path = f'{path}/assetfinder.txt'
    assetfinder_path = f'{path}/amass_subdomain.txt'
    with open(amass_path, 'r') as amass:
        amass_subdomains = set(amass)
    with open(assetfinder_path, 'r') as assetfinder:
        assetfinder_subdomains = set(assetfinder)
    combined = set(amass_subdomains|assetfinder_subdomains)
    with open(f'{path}/combined_subdomain.txt', 'w') as file:
        file.writelines(sorted(list(combined)))

def httprobe(asset_path):
    print('[-] Running HTTProbe')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/httprobe.txt', 'a')
    result = subprocess.run(['httprobe'], stdin=open(asset_path, 'r'), stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()

def gowitness(filePath):
    path = os.path.abspath(os.path.join(target,'gowitness'))
    os.chdir(path)
    with open(filePath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            subdomain = line.rstrip()
            print(f'[-] Running gowitness on {subdomain}')
            subprocess.run(['gowitness', '--timeout', '10', 'single', f'--url={subdomain}'], stdout=subprocess.PIPE, text=True)

if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    target = config["name"]
    print(f'[-] Preparing to Scan {target}')

    domains = []
    domains = config["domains"]
    dns = config["amass"]["dns"]
    prepare_dir(target)
    asset_finder(target, domains)
    amass(target, domains, dns)
    combine(target)

    if checkfile(subdomains):
         httprobe(subdomains)

    path = os.path.abspath(os.path.join(target))
    httprobe_path = f'{path}/httprobe.txt'
    if checkfile(httprobe_path):
        gowitness(httprobe_path)
    else:
        print("Looks like there's nothing left to scan")
        sys.exit()