{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}{{ $zone := envOrDefault "ZONE" "default" }}prometheus.remote_write "staging" {
  endpoint {
    url = "{{ $remote_url }}"
  }
}


{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}prometheus.scrape "{{$d.name}}" {
  targets = [
    { "__address__" = "localhost:12345", 
      "instance" = "{{$d.address}}", 
      "module" = "{{$d.module}}",
      {{ range $i, $elem := $d.labels }}"{{$elem.name}}" = "{{$elem.value}}",
      {{ end }}
    },
  ]

  forward_to = [prometheus.relabel.init_proxy_label.receiver]

  scrape_interval = "{{$d.interval}}"
  scrape_timeout = "{{$d.timeout}}"
  params          = { "target" = ["{{$d.address}}"], "module" = ["{{$d.module}}"], "walk_params" = ["{{$d.walk_params}}"] }
  metrics_path    = "/integrations/snmp/metrics"
}{{ end }}
{{ end }}

{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}prometheus.scrape "{{$d.name}}" {
  targets = [
    { "__address__" = "localhost:9290", 
      "instance" = "{{$d.task.address}}", 
      "module" = "{{$d.name}}",
      {{ range $i, $elem := $d.labels }}"{{$elem.name}}" = "{{$elem.value}}",
      {{ end }}
    },
  ]

  forward_to = [prometheus.relabel.ipmi_label.receiver]

  scrape_interval = "{{$d.scrape_interval}}"
  scrape_timeout = "{{$d.scrape_timeout}}"
  params          = { "target" = ["{{$d.task.address}}"], "module" = ["{{$d.name}}"] }
  metrics_path    = "/ipmi"
}{{ end }}
{{ end }}

prometheus.relabel "ipmi_label" {
  forward_to = [prometheus.relabel.init_proxy_label.receiver]

  rule {
    action        = "replace"
    target_label  = "dimension"
    source_labels = ["__name__","name"]
    regex         = "^(ipmi_fan_speed_rpm|ipmi_fan_speed_state|ipmi_power_state|ipmi_power_watts|ipmi_sensor_state|ipmi_sensor_value|ipmi_voltage_volts|ipmi_voltage_state);(.+)$"
    replacement   = "$1"
  }

  rule {
    action        = "replace"
    target_label  = "dimension"
    source_labels = ["__name__","collector"]
    regex         = "^(ipmi_up);(.+)$"
    replacement   = "$1"
  }

}

prometheus.relabel "init_proxy_label" {
  forward_to = [prometheus.remote_write.staging.receiver]

  rule {
    action        = "replace"
    target_label  = "zone"
    replacement   = "{{ $zone }}"
  }

  rule {
    action        = "replace"
    target_label  = "source"
    replacement   = "weops_proxy"
  }
}

logging {
  level  = "info"
  format = "logfmt"
}