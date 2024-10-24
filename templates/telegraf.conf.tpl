{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}{{ $zone := envOrDefault "ZONE" "default" }}[agent]
{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}
[[inputs.ipmi_sensor]]
timeout = {{if $d.scrape_timeout }}"{{ $d.scrape_timeout }}"{{else}}"60s"{{end}}
interval = {{if $d.scrape_interval }}"{{ $d.scrape_interval }}"{{else}}"60s"{{end}}
servers = ["{{$d.task.user}}:{{$d.task.pass}}@{{if eq $d.task.driver "LAN_2_0" }}lanplus{{else}}lan{{end}}({{$d.task.address}})"]
  [inputs.ipmi_sensor.tags]
    protocol = "ipmi"
    source = "telegraf"
    {{ range $i, $elem := $d.labels }}{{$elem.name}} = "{{$elem.value}}"
    {{ end }}
{{ end }}{{end}}

[[outputs.http]]
url = "{{ $remote_url }}"
data_format = "prometheusremotewrite"
[outputs.http.headers]
    Content-Type = "application/x-protobuf"
    Content-Encoding = "snappy"
    X-Prometheus-Remote-Write-Version = "0.1.0"