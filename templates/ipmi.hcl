template {
  source = "/app/templates/ipmi.conf.tpl"
  destination = "/app/config/ipmi.conf"
  command = "curl http://127.0.0.1:9290/-/reload || echo panic"
}