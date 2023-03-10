# Returns a list of free "working" proxies
# List of proxies generated by proxine
import requests, json, concurrent.futures, time, subprocess
from math import floor
from datetime import datetime
import os, string

# number of cpu virtual processors
NUMBER_OF_THREADS = 16
# url in which proxies will be tested on
TARGET_URL = "https://reddit.com"

# test proxy against TARGET_URL, if its successfull then add proxy to working proxy list
def testProxy(proxy):
    try:
        r = requests.get(TARGET_URL, proxies = {"http": proxy, "https": proxy}, timeout=2)
    except:
        print(f"Proxy {proxy} Failed!")
        pass
    else:
        if r.status_code == 200:
            print(f"Proxy {proxy} Succeded!")
            return proxy
    return False

# Check if the proxy list is older than 2 hours if it is then get a new proxy list
def checkForNewProxies():
    lastUpdate = 0
    if (os.path.exists("proxy.lst")):
        with open("proxy.lst", "r") as f:
            line = f.readline()
            if line != '':
                lastUpdate = float(line)
    timeSinceLastUpdate = time.time() - lastUpdate

    print(f"Time since last proxy update: {floor(timeSinceLastUpdate)}s")
    if timeSinceLastUpdate > 3600:
        print("Updating proxy list...")

        p = subprocess.Popen("bash proxine.sh https > ../proxy.lst", shell=True, cwd="./proxine/")
        p.wait()
        with open("proxy.lst", "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(str(time.time()).rstrip('\r\n') + '\n' + content)
        print("Finished updating proxy list")

# Test connection between proxies and target website, if its successfull then add the working proxy list 
def getWorkingProxyList():
    checkForNewProxies()
    
    proxyList = []
    lastProxyTest = -1

    if(os.path.exists("workingProxies.lst")):
        with open("workingProxies.lst", "r") as f:
            line = f.readline()
            if line != '':
                lastProxyTest = float(line)

    if time.time() - lastProxyTest < 3600:
        proxyList = open("workingProxies.lst", "r").read().splitlines()
        proxyList.pop(0) # remove timestamp

    else:
        numberOfWorkers = NUMBER_OF_THREADS + 4

        with open("proxy.lst", 'r') as f:
            proxies = f.read().splitlines()
            proxies.pop(0)
        
        proxies = proxies[:2000] # usefull for huge proxylists

        with concurrent.futures.ThreadPoolExecutor(max_workers=numberOfWorkers) as executor:
            results = executor.map(testProxy, proxies)
        
        for result in results:
            if result != False:
                proxyList.append(result)

        with open("workingProxies.lst", "w+") as f:
            f.write(str(time.time()) + "\n")
            for line in proxyList:
                f.write(line + "\n")

    print(f"Number of working proxies: {len(proxyList)}")
    return proxyList