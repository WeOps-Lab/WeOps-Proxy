{{ $zone := envOrDefault "ZONE" "default" }}
auths:
{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}{{ with $p := $d.param | parseYAML }}{{ range $key, $value := $p }}{{ $key | indent 2 }}:
{{ if eq $value.version 2 }}    version: 2
    community: {{ if $value.auth.community }}{{ $value.auth.community }}{{ else }}{{ "" }}{{ end }}
{{ else }}    version: 3
    username: {{ if $value.auth.username }}{{ $value.auth.username }}{{ else }}{{ "" }}{{ end }}
    auth_protocol: {{ if $value.auth.auth_protocol }}{{ $value.auth.auth_protocol }}{{ else }}{{ "" }}{{ end }}
    priv_protocol: {{ if $value.auth.priv_protocol }}{{ $value.auth.priv_protocol }}{{ else }}{{ "" }}{{ end }}
    priv_password: {{ if $value.auth.priv_password }}{{ $value.auth.priv_password }}{{ else }}{{ "" }}{{ end }}
    security_level: {{ if $value.auth.security_level }}{{ $value.auth.security_level }}{{ else }}{{ "" }}{{ end }}
    context_name: {{ if $value.auth.context_name }}{{ $value.auth.context_name }}{{ else }}{{ "" }}{{ end }}
    password: {{ if $value.auth.password }}{{ $value.auth.password }}{{ else }}{{ "" }}{{ end }}
{{ end }}
{{ end }}{{ end }}{{ end }}{{ end }}
