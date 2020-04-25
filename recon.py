#!/usr/bin/env python3

#
# Attempt at a Python web reconaissance tool
#
#    This program can be redistributed and/or modified under the terms of the
#    GNU General Public License, either version 3 of the License, or (at your
#    option) any later version.
#

# TODO Use Amass
# TODO Combine Amass and assetFinder Results
# TODO Provide intel output from Amass
# TODO Add DNS Takeover with Aquatone
# TODO Add more recon with wayback

import sys
import os
import argparse
import subprocess
import shutil

def checkFile(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def prepareDir(target):
    targetDir = os.path.abspath(os.path.join(target))
    os.makedirs(targetDir, exist_ok=True)
    screenShotDir = os.path.abspath(os.path.join(target, 'gowitness'))
    os.makedirs(screenShotDir, exist_ok=True)

def assetFinder(target):
    print(f'[-] Running assetfinder on {target}')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/assetfinder.txt', 'a')
    result = subprocess.run(['assetfinder', '--subs-only', target], stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()

# amass subdomain enumeration
#TODO wordlist?
#TODO 
def amass(target):
    print(f'[-] amass on {target}')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/amass_subdomain.txt', 'a')
    result = subprocess.run(['amass', 'enum', '-active', '-brute', stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()

#TODO amass IP intel on subdomains after comparing with asset finder

#TODO combine those subdomain results then send to httprobe

#TODO masscan results from amass intel make sure to cross reference domains from amass intel and assetfinder
# while adding domains from amass to list going to  gowitness or add domains from assetfinder to intel scan 
# for mass scan while

def httProbe(assetPath):
    print('[-] Running HTTProbe')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/httprobe.txt', 'a')
    result = subprocess.run(['httprobe'], stdin=open(assetPath, 'r'), stdout=subprocess.PIPE, text=True)
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
            # Change timeout to 10 for slow sites
            subprocess.run(['gowitness', '--timeout', '10', 'single', f'--url={subdomain}'], stdout=subprocess.PIPE, text=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Python Web Reconaissance Tool')
    parser.add_argument('target', action='store', help='hostname (e.g. example.com example2.com) to scan.', nargs="*")
    args = parser.parse_args()

    if not args.target:
        print('You must provide a target')
        sys.exit(1)
    elif len(args.target) > 1:
        print('You must only provide ONE target')
        sys.exit(1)
    else:
        target = args.target[0]
        print(f'[-] Preparing to Scan {target}')

    prepareDir(target)
    assetFinder(target)

    assetPath = f'{target}/assetfinder.txt'
    if checkFile(assetPath):
        httProbe(assetPath)

    path = os.path.abspath(os.path.join(target))
    httprobePath = f'{path}/httprobe.txt'
    if checkFile(httprobePath):
        gowitness(httprobePath)
    else:
        print("Looks like there's nothing left to scan")
        sys.exit()