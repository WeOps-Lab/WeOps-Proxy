{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}{{ $zone := envOrDefault "ZONE" "default" }}[agent]
  interval = "10s"
  round_interval = true
{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}
[[inputs.ipmi_sensor]]
timeout = {{if $d.timeout }}"{{ $d.timeout }}"{{else}}"60s"{{end}}
interval = {{if $d.interval }}"{{ $d.interval }}"{{else}}"60s"{{end}}
servers = ["{{$d.userid}}:{{$d.passowrd}}@lan({{$d.server}})"]
  [inputs.ipmi_sensor.tags]
    task_name = "{{$d.task_name}}"
{{ end }}{{end}}
[[outputs.file]]
files=["stdout"]

[[outputs.http]]
url = "{{ $remote_url }}"
data_format = "prometheusremotewrite"
[outputs.http.headers]
    Content-Type = "application/x-protobuf"
    Content-Encoding = "snappy"
    X-Prometheus-Remote-Write-Version = "0.1.0"