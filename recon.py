#!/usr/bin/env python3

#
# Attempt at a Python web reconaissance tool
#
#    This program can be redistributed and/or modified under the terms of the
#    GNU General Public License, either version 3 of the License, or (at your
#    option) any later version.
#

import sys
import os
import argparse
import subprocess

def checkFile(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def prepareDir(target):
    targetDir = os.path.abspath(os.path.join(target))
    os.makedirs(targetDir, exist_ok=True)
    screenShotDir = os.path.abspath(os.path.join(target, 'gowitness'))
    os.makedirs(screenShotDir, exist_ok=True)
    gobusterDir = os.path.abspath(os.path.join(target, 'gobuster'))
    os.makedirs(gobusterDir, exist_ok=True)

def assetFinder(target):
    print(f'[-] Running assetfinder on {target}')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/assetfinder.txt', 'a')
    result = subprocess.run(['assetfinder', target], stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()
    return (result.stdout).splitlines()

def httProbe(assetPath):
    print('[-] Running HTTProbe')
    path = os.path.abspath(os.path.join(target))
    output = open(f'{path}/httprobe.txt', 'a')
    result = subprocess.run(['httprobe'], stdin=open(assetPath, 'r'), stdout=subprocess.PIPE, text=True)
    output.write(result.stdout)
    output.close()
    return (result.stdout).splitlines()

def gobuster(filePath):
    for subdomain in subdomains:
        print(f'[-] Running gobuster on {subdomain}')
        result = subprocess.run(['gobuster', 'dir', '-q', '-w', 'wordlist.txt', subdomain], stdout=subprocess.PIPE, text=True)
        if result:
            output.write(result.stdout)
            path = os.path.abspath(os.path.join(target,'gobuster'))
            output = open(f'{path}/{subdomain}.txt', 'a')
            output.close()

def gowitness(filePath):
    path = os.path.abspath(os.path.join(target,'gobuster'))
    with open(filePath, 'r') as file:
        subdomains = list(set(file.read().replace('\n', '').splitlines()))
    for subdomain in subdomains:
        print(f'[-] Running gowitness on {subdomain}')
        result = subprocess.run(['gowitness', 'single', f'https://{subdomain}', '-d', path], stdout=subprocess.PIPE, text=True)
        if result:
            output.write(result.stdout)
            output = open(f'{path}/{subdomain}.txt', 'a')
            output.close()

    
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
        print(args.target)

    target = args.target[0]

    print(f'[-] Preparing to Scan {target}')
    prepareDir(target)
    subdomains = list(set(assetFinder(target)))
    print(subdomains)

    assetPath = f'{target}/assetfinder.txt'
    if checkFile(assetPath):
        httProbe(assetPath)

    httprobePath = f'{target}/httprobe.txt'
    if checkFile(httprobePath):
        gobuster(httprobePath)
    else:
        print("Looks like there's nothing left to scan")
        sys.exit()
    
    httprobePath = f'{target}/httprobe.txt'
    if checkFile(httprobePath):
        gowitness(httprobePath)