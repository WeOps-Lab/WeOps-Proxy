template {
  source = "./support-files/alert_rules.tpl"
  destination = "./config/alert_rules.yml"
  command = "curl -X POST http://prometheus:9090/-/reload || echo panic"
}