from enum import Enum
from string import Template
import consul
import yaml
import requests
import json


class WeOpsProxyClient(object):
    __consul = None
    __ipmi_template = """server: ${server}
userid: ${userid}
password: ${password}
timeout: ${timeout}
task_name: ${task_id}
interval: ${interval}
"""
    __snmp_v2_template = """interval: ${interval}
timeout: ${timeout}
name: ${task_id}
address: ${task_address}
module: ${task_module}
walk_params: ${task_id}

target: |
  - name: ${task_id}
    address: ${task_address}
    module: ${task_module}
    walk_params: ${task_id}

param: |
  ${task_id}:
    version: 2
    auth:
      community: ${community}
"""
    __snmp_v3_template = """interval: ${interval}
timeout: ${timeout}
name: ${task_id}
address: ${task_address}
module: ${task_module}
walk_params: ${task_id}

target: |
  - name: ${task_id}
    address: ${task_address}
    module: ${task_module}
    walk_params: ${task_id}

param: |
  ${task_id}:
    version: 3
    auth:
      username: ${username}
      security_level: ${security_level}
      password: ${password}
      auth_protocol: ${auth_protocol}
      priv_protocol: ${priv_protocol}
      priv_password: ${priv_password}
      context_name: ${context_name}
"""
    __consul_path_template = """weops/{}/{}/{}/{}"""
    __snmp_task_param = {
        "type": "zone",
        "module": "snmp"
    }
    __ipmi_task_param = {
        "type": "zone",
        "module": "ipmi"
    }
    __config_param = {
        "type": "global",
        "zone": "modules"
    }
    __metric_template = """record: ${record}
expr: ${expr}
"""

    class Action(Enum):
        Put = 1
        Get = 2
        Delete = 3

    class SNMPV3_Security_Level(Enum):
        noAuthNoPriv = "noAuthNoPriv"
        authNoPriv = "authNoPriv"
        authPriv = "authPriv"

    class SNMPV3_Auth_Protocol(Enum):
        MD5 = "MD5"
        SHA = "SHA"
        SHA224 = "SHA224"
        SHA256 = "SHA256"
        SHA384 = "SHA384"
        SHA512 = "SHA512"

    def __init__(self, consul_host, consul_port, consul_token=None) -> None:
        # """ToDO 添加连接校验"""
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.consul_token = consul_token
        self.__consul = consul.Consul(
            host=self.consul_host, port=self.consul_port)

    def _get_key(self, module, key, type, zone) -> str:
        return self.__consul_path_template.format(type, zone, module, key)
    
    def _get_ipmi_task(self, task_id, task_address, interval, timeout, userid, password) -> str:
        task_info = {
            "task_id": task_id,
            "task_address": task_address,
            "userid": userid,
            "password": password,
            "interval": interval,
            "timeout": timeout
        }
        return Template(self.__ipmi_template).safe_substitute(task_info)

    def _get_snmp_task(self, task_id, task_address, task_module, interval, timeout, auth) -> str:
        task_info = {
            "task_id": task_id,
            "task_address": task_address,
            "task_module": task_module,
            "interval": interval,
            "timeout": timeout
        }
        task_info.update(auth)
        if "community" in auth:
            return Template(self.__snmp_v2_template).safe_substitute(task_info)
        else:
            return Template(self.__snmp_v3_template).safe_substitute(task_info)

    def _runner(self, action, **params):
        if action == self.Action.Put:
            self.__consul.kv.put(
                params["key"], params["value"].encode('utf-8'))
        elif action == self.Action.Get:
            return self.__consul.kv.get(params["key"])
        elif action == self.Action.Delete:
            self.__consul.kv.delete(params["key"])

    def _generate_key(self, **params) -> str:
        if "zone" in params:
            if params["module"] == "snmp":
                params.update(self.__snmp_task_param)
            elif params["module"] == "ipmi":
                params.update(self.__ipmi_task_param)
            else:
                raise Exception("unexpected zone {}!", params["zone"])
        else:
            params.update(self.__config_param)
        return self._get_key(**params)

    def put_snmp_v2_task(self, zone, task_id, task_address, task_config, community, interval="60s", timeout="60s"):
        self._runner(self.Action.Put,
                     key=self._generate_key(zone=zone, key=task_id,module="snmp"),
                     value=self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                         "community": community
                     }, interval=interval, timeout=timeout))

    def put_snmp_v3_task(self, zone, task_id, task_address, task_config, username, security_level: SNMPV3_Security_Level, password, auth_protocol: SNMPV3_Auth_Protocol, priv_protocol, priv_password, context_name="", interval="60s", timeout="60s"):
        """snmp v3 params:
        username
        security_level
        password
        auth_protocol
        priv_protocol
        priv_password
        context_name
        """
        self._runner(self.Action.Put,
                     key=self._generate_key(zone=zone, key=task_id,module="snmp"),
                     value=self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                         "username": username,
                         "security_level": security_level,
                         "password": password,
                         "auth_protocol": auth_protocol,
                         "priv_protocol": priv_protocol,
                         "priv_password": priv_password,
                         "context_name": context_name
                     }, interval=interval, timeout=timeout))

    def delete_snmp_task(self, zone, task_id):
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(zone=zone, key=task_id))

    def get_snmp_task(self, zone, task_id) -> str:
        data = self._runner(action=self.Action.Get,
                            key=self._generate_key(zone=zone, key=task_id))
        try:
            return data[1]["Value"]
        except:
            raise Exception(f"snmp task {task_id} in zone {zone} does not exist!")

    def get_global_config(self, module, config_id) -> str:
        data = self._runner(action=self.Action.Get, key=self._generate_key(
            module=module, key=config_id))
        try:
            return data[1]["Value"]
        except:
            raise Exception(
                f"config {config_id} in module {module} does not exist!")

    def put_global_config(self, module, config_id, config):
        try:
            yaml.load(config, yaml.FullLoader)
        except Exception as e:
            raise e
        self._runner(self.Action.Put,
                     key=self._generate_key(module=module, key=config_id),
                     value=config)

    def delete_global_config(self, module, config_id):
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(module=module, key=config_id))

    def __list_consul_key(self):
        __consul_url = f"http://{self.consul_host}:{self.consul_port}/v1/kv/weops/access_points/?keys"
        response = requests.get(__consul_url)
        assert response.status_code == 200
        return json.loads(response.text)

    def get_access_points(self):
        paths = self.__list_consul_key()
        paths.remove('weops/access_points/')
        access_points = []
        for node in paths:
            data = self._runner(self.Action.Get, key=node)[1].get("Value")
            access_points.append(
                json.loads(data)
            )
        return access_points

    def put_metric(self, metric_record, metric_expr):
        path = "weops/global/metrics/{}".format(metric_record)
        self._runner(self.Action.Put,
                     key=path,
                     value=Template(self.__metric_template).safe_substitute({
                         "record": metric_record,
                         "expr": metric_expr
                     }))

    def get_metric(self, metric_record):
        return yaml.load(
            self._runner(
                self.Action.Get, key="weops/global/metrics/{}".format(metric_record))[1].get("Value"),
            yaml.FullLoader)

    def delete_metric(self, metric_record):
        self._runner(self.Action.Delete,
                     key="weops/global/metrics/{}".format(metric_record))
    
    def put_ipmi_task(self, zone, task_id, task_address, userid, password, interval="60s", timeout="60s"):
        self._runner(self.Action.Put,
                        key=self._generate_key(zone=zone, key=task_id,module="ipmi"),
                        value=self._get_ipmi_task(task_id=task_id, task_address=task_address, userid=userid, password=password, interval=interval, timeout=timeout))

    def get_ipmi_task(self, zone, task_id) -> str:
        data = self._runner(action=self.Action.Get,
                            key=self._generate_key(zone=zone, key=task_id, module="ipmi"))
        try:
            return data[1]["Value"]
        except:
            raise Exception(f"ipmi task {task_id} in zone {zone} does not exist!")
        

    def delete_ipmi_task(self, zone, task_id):
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(zone=zone, key=task_id, module="ipmi"))