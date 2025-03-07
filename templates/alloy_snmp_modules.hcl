template {
  source = "/app/templates/alloy_snmp_modules.yaml.tpl"
  destination = "/app/config/alloy_snmp_modules.yaml"
  command = "curl -sSL http://127.0.0.1:1234/-/reload || echo 'Failed to reload alloy_snmp_modules.yaml'"
}