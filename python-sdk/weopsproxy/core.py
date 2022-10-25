from enum import Enum
from string import Template
import consul
import yaml

class WeOpsProxyClient(object):
    __consul = None
    __snmp_v2_template = """
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
    __snmp_v3_template = """
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
    __task_param = {
        "type": "zone",
        "module": "snmp"
    }
    __config_param = {
        "type": "global",
        "zone": "modules"
    }

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
        self.__consul = consul.Consul(host=self.consul_host, port=self.consul_port)

    def _get_key(self, module, key, type, zone) -> str:
        return self.__consul_path_template.format(type, zone, module, key)

    def _get_snmp_task(self, task_id, task_address, task_module, auth) -> str:
        task_info = {
              "task_id": task_id,
              "task_address": task_address,
              "task_module": task_module,
        }
        task_info.update(auth)
        if "community" in auth:
          return Template(self.__snmp_v2_template).safe_substitute(task_info)
        else:
          return Template(self.__snmp_v3_template).safe_substitute(task_info)

    def _runner(self, action, **params):
        if action == self.Action.Put:
            self.__consul.kv.put(params["key"], params["value"].encode('utf-8'))
        elif action == self.Action.Get:
            return self.__consul.kv.get(params["key"])
        elif action == self.Action.Delete:
            self.__consul.kv.delete(params["key"])

    def _generate_key(self, **params) -> str:
        if "zone" in params:
            params.update(self.__task_param)
        else:
            params.update(self.__config_param)
        return self._get_key(**params)

    def put_snmp_v2_task(self, zone, task_id, task_address, task_config, community):
        self._runner(self.Action.Put,
                     key=self._generate_key(zone=zone, key=task_id),
                     value=self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                      "community": community
                     }))

    def put_snmp_v3_task(self, zone, task_id, task_address, task_config, username, security_level:SNMPV3_Security_Level, password, auth_protocol:SNMPV3_Auth_Protocol, priv_protocol, priv_password, context_name=""):
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
                     key = self._generate_key(zone=zone, key=task_id),
                     value = self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                      "username": username,
                      "security_level": security_level,
                      "password": password,
                      "auth_protocol": auth_protocol,
                      "priv_protocol": priv_protocol,
                      "priv_password": priv_password,
                      "context_name": context_name
                     }))

    def delete_snmp_task(self, zone, task_id):
        self._runner(action = self.Action.Delete,
                     key = self._generate_key(zone=zone, key=task_id))

    def get_snmp_task(self, zone, task_id) -> str:
        data=self._runner(action = self.Action.Get,
                            key = self._generate_key(zone=zone, key=task_id))
        try:
            return data[1]["Value"]
        except:
            raise Exception(f"task {task_id} in zone {zone} does not exist!")

    def get_global_config(self, module, config_id) -> str:
        data=self._runner(action = self.Action.Get, key = self._generate_key(
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