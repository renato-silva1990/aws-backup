# Aws Backup

## Descrição

Script que realiza a configuração completa do AWS Backup, pode criar ou remover os seguintes recursos: Backup Vault, Backup Plan, Backup Selection (Assigned Resources) e Backup Notification. É compatível com *EC2*, *S3*, *EBS*, *DynamoDB*, *RDS*, *Aurora*, *EFS*, *FSX (for Lustre / for Windows File Server)*, *Storage Gateway*, *DocumentDB* e *Neptune*.

## Pré-requisitos

- Ter o python instalado;
- Ter o boto3 instalado;
- Ter o awscli instalado;

## Parâmetros para execução

- `backup_vault_name`: Nome do cofre de backup
- `backup_plan_name`: Nome do plano de backup
- `rule_name`: Nome da regra associada ao plano de backup (caso seja criado seguindo o padrão da Solvimm deve ter o mesmo nome do backup plan)
- `schedule_cron_expression`: Expressão CRON em UTC especificando quando o Backup inicia uma job de backup.
- `backup_start_window`: Um valor em HORAS após o agendamento de um backup antes que um job seja cancelado se não for iniciado com êxito. 
- `backup_window`: Um valor em HORAS após um trabalho de backup ser iniciado com êxito antes de ser concluído ou será cancelado pelo Backup.
- `backup_retention_period`: Número de DIAS após a criação em que um recovery point é excluído.
- `windows_vss`: Defina como "enabled" para habilitar a opção de backup do Windows VSS ou defina como "disabled" para criar um backup regular.
- `backup_selection_name`: Nome do Selection associado ao plano de backup (caso seja criado seguindo o padrão da Solvimm deve ter o mesmo nome do backup plan)
- `condition_key`: A Key em um Key-Value pair. Por exemplo, na tag *Department: Accounting*, Department é a Key.
- `condition_value`: O value em um Key-Value pair. Por exemplo, na tag *Department: Accounting*, Accounting é o Value.

- Para mais detalhes sobre o padrão Solvimm para o AWS Backup, acesse: https://docs.google.com/document/d/1kb9xVHmj4bsjv-n-p8n0atWvpq2FMOGQMJ_fVHXPPuU/edit

## Execução
- Realizar o acesso programático via Leapp.
- Acesse a pasta do projeto via terminal e execute o seguinte comando:
	- `python3 aws_backup.py`
- Escolha entre os modos de criação ou de remoção.
- Passe os parâmetros solicitados (de acordo com o modo selecionado)