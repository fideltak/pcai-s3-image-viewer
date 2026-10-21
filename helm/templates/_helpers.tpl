{{- define "s3-image-viewer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "s3-image-viewer.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "s3-image-viewer.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- define "s3-image-viewer.labels" -}}
app.kubernetes.io/name: {{ include "s3-image-viewer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}
{{- define "s3-image-viewer.selectorLabels" -}}
app.kubernetes.io/name: {{ include "s3-image-viewer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
{{- define "s3-image-viewer.secretName" -}}
{{- default (printf "%s-s3" (include "s3-image-viewer.fullname" .)) .Values.s3.existingSecret -}}
{{- end -}}
