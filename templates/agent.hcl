template {
  source = "/app/templates/agent.conf.tpl"
  destination = "/app/config/agent.conf"
  command = "supervisorctl restart grafana-agent"
}