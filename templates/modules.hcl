template {
  source = "/app/templates/modules.yaml.tpl"
  destination = "/app/config/modules.yaml"
  command = "sh -c "supervisorctl -c /app/config/supervisord.conf  restart grafana-agent""
}