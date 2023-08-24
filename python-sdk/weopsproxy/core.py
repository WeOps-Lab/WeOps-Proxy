from enum import Enum
from string import Template
from typing import Optional
import consul
import yaml
import requests
import json


class WeOpsProxyClient(object):
    __consul = None
    __ipmi_template = """name: ${task_id}
scrape_interval: ${interval}
scrape_timeout: ${timeout}
task:
  address: ${task_address}
  user: ${userid}
  pass: ${password}
  driver: LAN_2_0
  timeout: 10000
labels:
${labels}
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

labels:
${labels}
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
labels:
${labels}
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
    __alert_template = """alert: ${alert}
expr: ${expr}
for: ${interval}
labels:
${labels}
annotations:
${annotations}"""

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

    def __init__(self, consul_host: str, consul_port: str, consul_token: str=None) -> None:
        # """ToDO 添加连接校验"""
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.consul_token = consul_token
        self.__consul = consul.Consul(
            host=self.consul_host, port=self.consul_port)

    def _get_key(self, module: str, key: str, type: str, zone: str) -> str:
        return self.__consul_path_template.format(type, zone, module, key)

    def _get_ipmi_task(self, task_id: str, task_address: str, interval: str, timeout: str, userid: str, password: str, labels_str: str) -> str:
        task_info = {
            "task_id": task_id,
            "task_address": task_address,
            "userid": userid,
            "password": password,
            "interval": interval,
            "timeout": timeout,
            "labels": labels_str
        }
        return Template(self.__ipmi_template).safe_substitute(task_info)

    def _get_snmp_task(self, task_id: str, task_address: str, task_module: str, interval: str, timeout: str, labels_str: str, auth: dict) -> str:
        task_info = {
            "task_id": task_id,
            "task_address": task_address,
            "task_module": task_module,
            "interval": interval,
            "timeout": timeout,
            "labels": labels_str
        }
        task_info.update(auth)
        if "community" in auth:
            return Template(self.__snmp_v2_template).safe_substitute(task_info)
        else:
            return Template(self.__snmp_v3_template).safe_substitute(task_info)

    def _runner(self, action, **params) -> Optional[str]:
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

    def _build_label_str(sef, labels: dict) -> None:
        labels_str = ""
        for name, value in labels.items():
            labels_str += '- name: {}\n  value: {}\n'.format(name, value)
        return labels_str

    def _build_alert_label_str(sef, labels: dict) -> None:
        labels_str = ""
        for name, value in labels.items():
            labels_str += '  {}: {}\n'.format(name, value)
        return labels_str

    def put_snmp_v2_task(self, zone: str, task_id: str, task_address: str, task_config: str, community: str, labels: dict={}, interval: str="60s", timeout: str="60s") -> None:
        labels_str = self._build_label_str(labels)
        self._runner(self.Action.Put,
                     key=self._generate_key(
                         zone=zone, key=task_id, module="snmp"),
                     value=self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                         "community": community
                     }, labels_str=labels_str, interval=interval, timeout=timeout))

    def put_snmp_v3_task(self, zone: str, task_id: str, task_address: str, task_config: str, username: str, security_level: SNMPV3_Security_Level, password: str, auth_protocol: SNMPV3_Auth_Protocol, priv_protocol: str, priv_password: str, labels: dict={}, context_name: str="", interval: str="60s", timeout: str="60s") -> None:
        """snmp v3 params:
        username
        security_level
        password
        auth_protocol
        priv_protocol
        priv_password
        context_name
        """
        labels_str = self._build_label_str(labels)
        self._runner(self.Action.Put,
                     key=self._generate_key(
                         zone=zone, key=task_id, module="snmp"),
                     value=self._get_snmp_task(task_id=task_id, task_address=task_address, task_module=task_config, auth={
                         "username": username,
                         "security_level": security_level,
                         "password": password,
                         "auth_protocol": auth_protocol,
                         "priv_protocol": priv_protocol,
                         "priv_password": priv_password,
                         "context_name": context_name
                     }, labels_str=labels_str, interval=interval, timeout=timeout))

    def delete_snmp_task(self, zone: str, task_id: str) -> None:
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(zone=zone, module="snmp", key=task_id))

    def get_snmp_task(self, zone: str, task_id: str) -> str:
        data = self._runner(action=self.Action.Get,
                            key=self._generate_key(zone=zone, module="snmp", key=task_id))
        try:
            return data[1]["Value"]
        except:
            raise Exception(
                f"snmp task {task_id} in zone {zone} does not exist!")

    def get_global_config(self, module: str, config_id: str) -> str:
        data = self._runner(action=self.Action.Get, key=self._generate_key(
            module=module, key=config_id))
        try:
            return data[1]["Value"]
        except:
            raise Exception(
                f"config {config_id} in module {module} does not exist!")

    def put_global_config(self, module: str, config_id: str, config: str) -> None:
        try:
            yaml.load(config, yaml.FullLoader)
        except Exception as e:
            raise e
        self._runner(self.Action.Put,
                     key=self._generate_key(module=module, key=config_id),
                     value=config)

    def delete_global_config(self, module, config_id) -> None:
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(module=module, key=config_id))

    def __list_consul_key(self) -> str:
        __consul_url = f"http://{self.consul_host}:{self.consul_port}/v1/kv/weops/access_points/?keys"
        response = requests.get(__consul_url)
        assert response.status_code == 200
        return json.loads(response.text)

    def put_access_points(self, ip: str, name: str, zone: str, port: int) -> None:
        self._runner(self.Action.Put,
                     key=f"weops/access_points/{name}",
                     value= json.dumps({
                         "ip": ip,
                         "name": name,
                         "zone": zone,
                         "port": port
                     }))

    def get_access_points(self) -> str:
        paths = set(self.__list_consul_key())
        paths.discard('weops/access_points/')
        access_points = []
        for node in paths:
            data = self._runner(self.Action.Get, key=node)[1].get("Value")
            access_points.append(
                json.loads(data)
            )
        return access_points

    def put_metric(self, metric_record: str, metric_expr: str) -> None:
        path = "weops/global/metrics/{}".format(metric_record)
        self._runner(self.Action.Put,
                     key=path,
                     value=Template(self.__metric_template).safe_substitute({
                         "record": metric_record,
                         "expr": metric_expr
                     }))

    def get_metric(self, metric_record: str) -> str:
        return yaml.load(
            self._runner(
                self.Action.Get, key="weops/global/metrics/{}".format(metric_record))[1].get("Value"),
            yaml.FullLoader)

    def delete_metric(self, metric_record: str) -> None:
        self._runner(self.Action.Delete,
                     key="weops/global/metrics/{}".format(metric_record))

    def put_ipmi_task(self, zone: str, task_id: str, task_address: str, userid: str, password: str, labels: dict={}, interval: str="60s", timeout: str="60s") -> None:
        labels_str = self._build_label_str(labels)
        self._runner(self.Action.Put,
                     key=self._generate_key(
                         zone=zone, key=task_id, module="ipmi"),
                     value=self._get_ipmi_task(task_id=task_id, task_address=task_address, userid=userid, password=password, labels_str=labels_str, interval=interval, timeout=timeout))

    def get_ipmi_task(self, zone: str, task_id: str) -> str:
        data = self._runner(action=self.Action.Get,
                            key=self._generate_key(zone=zone, key=task_id, module="ipmi"))
        try:
            return data[1]["Value"]
        except:
            raise Exception(
                f"ipmi task {task_id} in zone {zone} does not exist!")

    def delete_ipmi_task(self, zone: str, task_id: str) -> None:
        self._runner(action=self.Action.Delete,
                     key=self._generate_key(zone=zone, key=task_id, module="ipmi"))

    def put_alert(self, alert_record: str, alert_expr: str, interval: str="3m", labels: dict={}, annotations: dict={}) -> None:
        path = "weops/global/alert/{}".format(alert_record)
        alert_labels_str = self._build_alert_label_str(labels=labels)
        alert_annotations_str = self._build_alert_label_str(labels=annotations)
        print(Template(self.__alert_template).safe_substitute({
            "alert": alert_record,
            "expr": alert_expr,
            "labels": alert_labels_str,
            "annotations": alert_annotations_str
        }))
        self._runner(self.Action.Put,
                     key=path,
                     value=Template(self.__alert_template).safe_substitute({
                         "alert": alert_record,
                         "expr": alert_expr,
                         "interval": interval,
                         "labels": alert_labels_str,
                         "annotations": alert_annotations_str
                     }))

    def delete_alert(self, alert_record: str) -> None:
        path = "weops/global/alert/{}".format(alert_record)
        self._runner(action=self.Action.Delete, key=path)

    def get_alert(self, alert_record: str) -> None:
        path = "weops/global/alert/{}".format(alert_record)
        data = self._runner(action=self.Action.Get, key=path)
        try:
            return data[1]["Value"]
        except:
            raise Exception(f"alert {alert_record} dose not exist")