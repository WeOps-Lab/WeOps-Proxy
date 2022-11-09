import pytest
from weopsproxy.core import WeOpsProxyClient

consul_ip="10.10.42.197"
consul_port="8500"
cisco_snmp_config = """walk:
- 1.3.6.1.2.1.14.10.1.3
- 1.3.6.1.2.1.14.10.1.6
- 1.3.6.1.2.1.15.3.1.1
- 1.3.6.1.2.1.15.3.1.2
- 1.3.6.1.2.1.2.2.1.10
- 1.3.6.1.2.1.2.2.1.11
- 1.3.6.1.2.1.2.2.1.13
- 1.3.6.1.2.1.2.2.1.14
- 1.3.6.1.2.1.2.2.1.16
- 1.3.6.1.2.1.2.2.1.17
- 1.3.6.1.2.1.2.2.1.19
- 1.3.6.1.2.1.2.2.1.2
- 1.3.6.1.2.1.2.2.1.20
- 1.3.6.1.2.1.2.2.1.7
- 1.3.6.1.2.1.2.2.1.8
- 1.3.6.1.2.1.31.1.1.1.15
- 1.3.6.1.2.1.31.1.1.1.2
- 1.3.6.1.2.1.31.1.1.1.3
- 1.3.6.1.2.1.31.1.1.1.4
- 1.3.6.1.2.1.31.1.1.1.5
- 1.3.6.1.4.1.2011.10.2.6.1.1.1.1.6
- 1.3.6.1.4.1.9.9.117.1.2.1.1.1
- 1.3.6.1.4.1.9.9.13.1.3.1.2
- 1.3.6.1.4.1.9.9.13.1.3.1.3
- 1.3.6.1.4.1.9.9.13.1.3.1.6
- 1.3.6.1.4.1.9.9.13.1.4.1.2
- 1.3.6.1.4.1.9.9.13.1.4.1.3
- 1.3.6.1.4.1.9.9.13.1.5.1.2
- 1.3.6.1.4.1.9.9.13.1.5.1.3
- 1.3.6.1.4.1.9.9.48.1.1.1.2
- 1.3.6.1.4.1.9.9.48.1.1.1.5
- 1.3.6.1.4.1.9.9.48.1.1.1.6
get:
- 1.3.6.1.2.1.1.3.0
metrics:
- name: cw_CiscoSwitch_sysUpTime
  oid: 1.3.6.1.2.1.1.3
  type: gauge
  help: 设备运行时间
- name: cw_CiscoSwitch_ospfNbrState
  oid: 1.3.6.1.2.1.14.10.1.6
  type: gauge
  help: 可用性
  indexes:
  - labelname: ospfNbrIpAddr
    type: InetAddressIPv4
  - labelname: ospfNbrAddressLessIndex
    type: gauge
  lookups:
  - labels:
    - ospfNbrIpAddr
    - ospfNbrAddressLessIndex
    labelname: ospfNbrRtrId
    oid: 1.3.6.1.2.1.14.10.1.3
    type: InetAddressIPv4
  enum_values:
    1: down
    2: attempt
    3: init
    4: twoWay
    5: exchangeStart
    6: exchange
    7: loading
    8: full
- name: cw_CiscoSwitch_bgpPeerState
  oid: 1.3.6.1.2.1.15.3.1.2
  type: gauge
  help: BGP状态
  indexes:
  - labelname: bgpPeerRemoteAddr
    type: InetAddressIPv4
  lookups:
  - labels:
    - bgpPeerRemoteAddr
    labelname: bgpPeerIdentifier
    oid: 1.3.6.1.2.1.15.3.1.1
    type: InetAddressIPv4
  enum_values:
    1: idle
    2: connect
    3: active
    4: opensent
    5: openconfirm
    6: established
- name: cw_CiscoSwitch_ifInOctets
  oid: 1.3.6.1.2.1.2.2.1.10
  type: counter
  help: 接收流量
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifInUcastPkts
  oid: 1.3.6.1.2.1.2.2.1.11
  type: counter
  help: 单播入包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifInDiscards
  oid: 1.3.6.1.2.1.2.2.1.13
  type: counter
  help: 接收丢包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifInErrors
  oid: 1.3.6.1.2.1.2.2.1.14
  type: counter
  help: 接收错包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutOctets
  oid: 1.3.6.1.2.1.2.2.1.16
  type: counter
  help: 发送流量
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutUcastPkts
  oid: 1.3.6.1.2.1.2.2.1.17
  type: counter
  help: 单播出包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutDiscards
  oid: 1.3.6.1.2.1.2.2.1.19
  type: counter
  help: 发送丢包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutErrors
  oid: 1.3.6.1.2.1.2.2.1.20
  type: counter
  help: 发送错包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifAdminStatus
  oid: 1.3.6.1.2.1.2.2.1.7
  type: gauge
  help: 接口管理状态
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
  enum_values:
    1: up
    2: down
    3: testing
- name: cw_CiscoSwitch_ifOperStatus
  oid: 1.3.6.1.2.1.2.2.1.8
  type: gauge
  help: 接口操作状态
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
  enum_values:
    1: up
    2: down
    3: testing
    4: unknown
    5: dormant
- name: cw_CiscoSwitch_ifHighSpeed
  oid: 1.3.6.1.2.1.31.1.1.1.15
  type: gauge
  help: 接口带宽
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifInMulticastPkts
  oid: 1.3.6.1.2.1.31.1.1.1.2
  type: counter
  help: 多播入包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifInBroadcastPkts
  oid: 1.3.6.1.2.1.31.1.1.1.3
  type: counter
  help: 广播入包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutMulticastPkts
  oid: 1.3.6.1.2.1.31.1.1.1.4
  type: counter
  help: 多播出包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ifOutBroadcastPkts
  oid: 1.3.6.1.2.1.31.1.1.1.5
  type: counter
  help: 广播出包数
  indexes:
  - labelname: ifIndex
    type: gauge
  lookups:
  - labels:
    - ifIndex
    labelname: ifDescr
    oid: 1.3.6.1.2.1.2.2.1.2
    type: DisplayString
- name: cw_CiscoSwitch_h3cEntityExtCpuUsage
  oid: 1.3.6.1.4.1.2011.10.2.6.1.1.1.1.6
  type: gauge
  help: CPU使用率
  indexes:
  - labelname: h3cEntityExtPhysicalIndex
    type: gauge
- name: cw_CiscoSwitch_cefcModuleAdminStatus
  oid: 1.3.6.1.4.1.9.9.117.1.2.1.1.1
  type: gauge
  help: 模块操作状态
  indexes:
  - labelname: entPhysicalIndex
    type: gauge
  enum_values:
    1: enabled
    2: disabled
    3: reset
    4: outOfServiceAdmin
- name: cw_CiscoSwitch_ciscoEnvMonTemperatureStatusValue
  oid: 1.3.6.1.4.1.9.9.13.1.3.1.3
  type: gauge
  help: 传感器温度
  indexes:
  - labelname: ciscoEnvMonTemperatureStatusIndex
    type: gauge
  lookups:
  - labels:
    - ciscoEnvMonTemperatureStatusIndex
    labelname: ciscoEnvMonTemperatureStatusDescr
    oid: 1.3.6.1.4.1.9.9.13.1.3.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ciscoEnvMonTemperatureState
  oid: 1.3.6.1.4.1.9.9.13.1.3.1.6
  type: gauge
  help: 温度传感器状态
  indexes:
  - labelname: ciscoEnvMonTemperatureStatusIndex
    type: gauge
  lookups:
  - labels:
    - ciscoEnvMonTemperatureStatusIndex
    labelname: ciscoEnvMonTemperatureStatusDescr
    oid: 1.3.6.1.4.1.9.9.13.1.3.1.2
    type: DisplayString
  enum_values:
    1: normal
    2: warning
    3: critical
    4: shutdown
    5: notPresent
    6: notFunctioning
- name: cw_CiscoSwitch_ciscoEnvMonFanState
  oid: 1.3.6.1.4.1.9.9.13.1.4.1.3
  type: gauge
  help: 风扇状态
  indexes:
  - labelname: ciscoEnvMonFanStatusIndex
    type: gauge
  lookups:
  - labels:
    - ciscoEnvMonFanStatusIndex
    labelname: ciscoEnvMonFanStatusDescr
    oid: 1.3.6.1.4.1.9.9.13.1.4.1.2
    type: DisplayString
  enum_values:
    1: normal
    2: warning
    3: critical
    4: shutdown
    5: notPresent
    6: notFunctioning
- name: cw_CiscoSwitch_ciscoEnvMonSupplyState
  oid: 1.3.6.1.4.1.9.9.13.1.5.1.3
  type: gauge
  help: 电源状态
  indexes:
  - labelname: ciscoEnvMonSupplyStatusIndex
    type: gauge
  lookups:
  - labels:
    - ciscoEnvMonSupplyStatusIndex
    labelname: ciscoEnvMonSupplyStatusDescr
    oid: 1.3.6.1.4.1.9.9.13.1.5.1.2
    type: DisplayString
  enum_values:
    1: normal
    2: warning
    3: critical
    4: shutdown
    5: notPresent
    6: notFunctioning
- name: cw_CiscoSwitch_ciscoMemoryPoolUsed
  oid: 1.3.6.1.4.1.9.9.48.1.1.1.5
  type: gauge
  help: 已用内存
  indexes:
  - labelname: ciscoMemoryPoolType
    type: gauge
  lookups:
  - labels:
    - ciscoMemoryPoolType
    labelname: ciscoMemoryPoolName
    oid: 1.3.6.1.4.1.9.9.48.1.1.1.2
    type: DisplayString
- name: cw_CiscoSwitch_ciscoMemoryPoolFree
  oid: 1.3.6.1.4.1.9.9.48.1.1.1.6
  type: gauge
  help: 剩余内存
  indexes:
  - labelname: ciscoMemoryPoolType
    type: gauge
  lookups:
  - labels:
    - ciscoMemoryPoolType
    labelname: ciscoMemoryPoolName
    oid: 1.3.6.1.4.1.9.9.48.1.1.1.2
    type: DisplayString
"""

class TestClass:
    def test_初始化client(self):
        WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )

    def test_生成conul的key(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        keys = ["cisco_cw", "h3c_cw", "huawei_cw"]
        for a in keys:
            assert client._generate_key(
                zone="default", key=a) == f"weops/zone/default/snmp/{a}", f"snmp_task key生成失败"
            assert client._generate_key(
                module="snmp", key=a) == f"weops/global/modules/snmp/{a}", f"snmp_module生成失败"

    def test_生成snmp采集任务的values(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client._get_snmp_task(task_id="cisco_cw", task_address="192.168.165.200", task_module="cisco_cw", auth={
            "username": "cisco123",
            "security_level": "AuthNoPriv",
            "password": "mypass123456",
            "auth_protocol": "SHA",
            "priv_protocol": "DES",
            "priv_password": "pass123456",
            "context_name": ""
        })

    def test_添加snmp_v2任务(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.put_snmp_v2_task(zone="default",
                                task_id="cisco_v2",
                                task_address="192.168.165.200",
                                task_config="cisco_switch",
                                community="cisco")

    def test_添加snmp_v3任务(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.put_snmp_v3_task(zone="default", task_id="cisco_v3", task_address="192.168.165.200", task_config="cisco_cw",
                                username="cisco123",
                                security_level="authPriv",
                                password="mypass123456",
                                auth_protocol="SHA",
                                priv_protocol="DES",
                                priv_password="pass123456",
                                context_name="")

    def test_查询snmp任务(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.get_snmp_task(zone="default", task_id="cisco_v2")
        client.get_snmp_task(zone="default", task_id="cisco_v3")

    def test_删除snmp任务(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.delete_snmp_task(zone="default", task_id="cisco_v2")
        client.delete_snmp_task(zone="default", task_id="cisco_v3")

    def test_创建全局配置(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.put_global_config(module="snmp", config_id="cisco_cw", config=cisco_snmp_config)

    def test_查询全局配置(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.get_global_config(module="snmp", config_id="cisco_cw")

    def test_删除全局配置(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        client.delete_global_config(module="snmp", config_id="h3c")
    
    def test_获取接入点(self):
        client = WeOpsProxyClient(
            consul_host=consul_ip,
            consul_port=consul_port
        )
        print(client.get_access_points())