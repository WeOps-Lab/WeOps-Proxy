template {
  source = "/app/templates/alloy.conf.tpl"
  destination = "/app/config/alloy.conf"
  command = "curl -sSL http://127.0.0.1:1234/-/reload || echo 'Failed to reload alloy.conf'"
}