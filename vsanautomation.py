import vsanmgmtObjects
import vsanapiutils
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim, vmodl, VmomiSupport
import pyVim.task
from pyVim.task import WaitForTask
import sys
import ssl
import time
import atexit
import ssl
import re
import argparse
import getpass



# This function will connect to vcenter and pass the ClusterName Variable.
def getClusterInstance(ClusterName, serviceInstance):
    content = serviceInstance.RetrieveContent()
    searchIndex = content.searchIndex
    datacenters = content.rootFolder.childEntity

    # Look for the cluster in each datacenter attached to vCenter
    for datacenter in datacenters:
        cluster = searchIndex.FindChild(datacenter.hostFolder, clusterName)
        if cluster is not None:
            return cluster
    return None
    
# This function will CollectMutiple object in Vcenter and store them for further use.
def CollectMultiple(content, objects, parameters, handleNotFound=True):
    if len(objects) == 0:
        return {}
    result = None
    pc = content.propertyCollector
    propSet = [vim.PropertySpec(
        type=objects[0].__class__,
        pathSet=parameters
    )]

    while result == None and len(objects) > 0:
        try:
            objectSet = []
            for obj in objects:
                objectSet.append(vim.ObjectSpec(obj=obj))
            specSet = [vim.PropertyFilterSpec(objectSet=objectSet, propSet=propSet)]
            result = pc.RetrieveProperties(specSet=specSet)
        except vim.ManagedObjectNotFound as ex:
            objects.remove(ex.obj)
            result = None

    out = {}
    for x in result:
        out[x.obj] = {}
        for y in x.propSet:
            out[x.obj][y.name] = y.val
    return out    

# Simple Math function needed for vsan automation.

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)    
