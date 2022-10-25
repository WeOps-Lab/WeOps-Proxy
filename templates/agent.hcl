template {
  source = "/app/templates/agent.conf.tpl"
  destination = "/app/config/agent.conf"
  command = "sh -c "supervisorctl -c /app/config/supervisord.conf  restart grafana-agent""
}