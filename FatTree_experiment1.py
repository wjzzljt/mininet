from mininet.net  import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.cli  import CLI
from mininet.log  import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess   import call
def myNetwork():
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')
    info('*** Adding switches \n')
    # 添加 core switches
    core=[None]*2
    aggregation=[None]*4
    edge=[None]*4
    cnt = int(0)
    for i in range(2):
        core[i]=[None]*2
        for j in range(2):
            core[i][j]=net.addSwitch('c%s'% cnt,cls=OVSKernelSwitch)
            cnt += 1
    # 添加 aggregation switches
    cnt = 0
    for i in range(4):
       aggregation[i]=[None]*2
       for j in range(2):
            aggregation[i][j]=net.addSwitch('a%s'% cnt,cls=OVSKernelSwitch)
            cnt += 1
    # 添加 egde switches
    cnt = 0
    for i in range(4):
        edge[i]=[None]*(2)
        for j in range(2):
            edge[i][j]=net.addSwitch('e%s'% cnt,cls=OVSKernelSwitch)
            cnt += 1
    # 添加链路 between core and aggregation switches
    info('*** Adding links \n')
    for i in range(2):
         for j in range(2):
             for l in range(k):
                 net.addLink(core[i][j],aggregation[l][i]) 
    # 添加链路 between aggregation and edge switches
    for i in range(4):
         for j in range(2):
             for l in range(2):
                 net.addLink(aggregation[i][j], edge[i][l])
    # 添加hosts 和 链路
    info('*** Adding hosts \n')
    cnt = 0
    for i in range(4):
        for j in range(2):
             for l in range(2):
                 host=net.addHost('h%s'% cnt,cls=Host,ip='10.%s.%s.%s'%(i,j,l+2),defaultRoute=None)
                 net.addLink(edge[i][j],host)
                 cnt += 1
    info('***start network\n')
    net.build()
    info('***start controller\n')
    for controller in net.controllers:
         controller.start()
         info('***start switches and allocate IP address\n')
    cnt = 0
    for i in range(2):
         for j in range(2):
             core[i][j].start([])
             core[i][j].cmd('ifconfig c%s 10.%s.%s.%s'%(cnt,k,i+1,j+1))
             cnt += 1
    cnt = 0
    for i in range(4):
         for j in range(2):
             aggregation[i][j].start([])
             edge[i][j].start([])
             aggregation[i][j].cmd('ifconfig a%s 10.%s.%s.1'%(cnt, i, j+2))
             edge[i][j].cmd('ifconfig e%s 10.%s.%s.1'%(cnt, i, j))
             cnt += 1
    info('***Post configure swithces\n')
    # 为core switches添加流表
    cnt = 0
    for i in range(2):
        for j in range(2):
            for pod in range(4):
                core[i][j].cmd(r'ovs-ofctl add-flow c%s "dl_type=0x806,arp_tpa=10.%d.0.0/16,actions=output:%d"'%(cnt,pod,pod+1))
                core[i][j].cmd(r'ovs-ofctl add-flow c%s "dl_type=0x800,nw_dst=10.%d.0.0/16,actions=output:%d"'%(cnt,pod,pod+1))
        cnt += 1
    # 为aggregation switches添加流表
    cnt = 0
    for i in range(4):
        for j in range(2):
            for switch in range(2):
                   aggregation[i][j].cmd(r'ovs-ofctl add-flow a%s "dl_type=0x806,arp_tpa=10.%d.%d.0/24,actions=output:%d"'%(cnt,i,switch,switch+3))
                   aggregation[i][j].cmd(r'ovs-ofctl add-flow a%s "dl_type=0x800,nw_dst=10.%d.%d.0/24,actions=output:%d"'%(cnt,i,switch,switch+3))
            for pod in range(4):
                   if(pod != i):
                       for switch in range(2):
                           for hid in range(2):
                               aggregation[i][j].cmd(r'ovs-ofctl add-flow a%s "dl_type=0x806,arp_tpa=10.%d.%d.%d,actions=output:%d"'%(cnt, pod, switch, hid+2, (hid+j)%2+1))
                               aggregation[i][j].cmd(r'ovs-ofctl add-flow a%s "dl_type=0x800,nw_dst=10.%d.%d.%d,actions=output:%d"'%(cnt, pod, switch, hid+2, (hid+j)%2+1))
            cnt += 1
     # 为edge switches添加流表
    cnt = 0
    for i in range(4):
        for j in range(2):
            for hid in range(2):
                edge[i][j].cmd(r'ovs-ofctl add-flow e%s "dl_type=0x806,arp_tpa=10.%d.%d.%d,actions=output:%d"'%(cnt,i,j,hid+2,hid+2+1))
                edge[i][j].cmd(r'ovs-ofctl add-flow e%s "dl_type=0x800,nw_dst=10.%d.%d.%d,actions=output:%d"'%(cnt,i,j,hid+2,hid+2+1))
            for pod in range(k):
                for switch in range(2):
                    if(pod != i or switch != j):
                        for hid in range(2):
                            edge[i][j].cmd(r'ovs-ofctl add-flow e%s "dl_type=0x806,arp_tpa=10.%d.%d.%d,actions=output:%d"'%(cnt, pod, switch, hid+2, (hid+j)%2+1))
                            edge[i][j].cmd(r'ovs-ofctl add-flow e%s "dl_type=0x800,nw_dst=10.%d.%d.%d,actions=output:%d"'%(cnt, pod, switch, hid+2, (hid+j)%2+1))
            cnt += 1
    info('*** Enable the Fat Tree \n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
