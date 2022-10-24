template {
  source = "/app/templates/modules.yaml.tpl"
  destination = "/app/config/modules.yaml"
  command = "supervisorctl restart grafana-agent"
}