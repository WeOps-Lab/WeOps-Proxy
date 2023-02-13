import pytest
from weopsproxy.core import WeOpsProxyClient
from test_env import *

class TestClass:
    def test_初始化client(self):
        WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )

    def test_生成conul的key(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        keys = ["cisco_cw", "h3c_cw", "huawei_cw"]
        for a in keys:
            assert client._generate_key(
                zone="default", module="snmp", key=a) == f"weops/zone/default/snmp/{a}", f"snmp_task key生成失败"
            assert client._generate_key(
                module="snmp", key=a) == f"weops/global/modules/snmp/{a}", f"snmp_module生成失败"
        assert client._generate_key(zone="default",module="ipmi",key="ipmi_test") == f"weops/zone/default/ipmi/ipmi_test"

    def test_生成snmp采集任务的values(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client._get_snmp_task(task_id="cisco_cw", task_address="192.168.165.200", task_module="cisco_cw", interval="60s",timeout="60s",auth={
            "username": "cisco123",
            "security_level": "AuthNoPriv",
            "password": "mypass123456",
            "auth_protocol": "SHA",
            "priv_protocol": "DES",
            "priv_password": "pass123456",
            "context_name": ""
        })
    
    def test_生产ipmi采集任务的vaules(self):
      client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
      client._get_ipmi_task(task_id="ipmi_task_1",task_address="10.10.10.10",userid="USERID",password="password",interval="60s",timeout="60s")

    def test_添加snmp_v2任务(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.put_snmp_v2_task(zone="default",
                                task_id="cisco_v2",
                                task_address="192.168.165.200",
                                task_config="cisco_cw",
                                labels={"instance_name":"instance","instance_value":"114514"},
                                community="cisco")

    def test_添加snmp_v3任务(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
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
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.get_snmp_task(zone="default", task_id="cisco_v2")
        client.get_snmp_task(zone="default", task_id="cisco_v3")

    def test_创建全局配置(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.put_global_config(
            module="snmp", config_id="cisco_cw", config=CISCO_SNMP_CONFIG)

    def test_查询全局配置(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.get_global_config(module="snmp", config_id="cisco_cw")

    def test_删除全局配置(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.delete_global_config(module="snmp", config_id="h3c")

    def test_获取接入点(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        print(client.get_access_points())

    def test_写入指标(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.put_metric(metric_record="cw_export_up",metric_expr="""irate(cw_CiscoSwitch_ifInOctets{module="cisco_switch"}[1m])""")
    
    def test_获取指标(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        print(client.get_metric(metric_record="cw_export_up"))

    def test_删除指标(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.delete_metric(metric_record="cw_export_up")

    def test_创建IPMI监控任务(self):
      client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
      client.put_ipmi_task(task_id="test_ipmi_1",task_address=IPMI_IP,userid=IPMI_USER,password=IPMI_PASSWORD,zone="default")
    
    def test_获取IPMI监控任务(self):
      client = WeOpsProxyClient(
        consul_host=CONSUL_IP,
        consul_port=CONSUL_PORT
      )
      client.get_ipmi_task(zone="default",task_id="test_ipmi_1")
    
    def test_删除IPMI监控任务(self):
      client = WeOpsProxyClient(
        consul_host=CONSUL_IP,
        consul_port=CONSUL_PORT
      )
      client.delete_ipmi_task(zone="default",task_id="test_ipmi_1")
    
    def test_删除snmp任务(self):
        client = WeOpsProxyClient(
            consul_host=CONSUL_IP,
            consul_port=CONSUL_PORT
        )
        client.delete_snmp_task(zone="default", task_id="cisco_v2")
        client.delete_snmp_task(zone="default", task_id="cisco_v3")