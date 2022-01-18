import boto3
from subprocess import check_output
from botocore.exceptions import ClientError
import sys
client = boto3.client('backup')
kms_client = boto3.client('kms')
iam_client = boto3.client('iam')
sns_client = boto3.client('sns')
sts_client = boto3.client('sts')

#------------------------------------------------------------------------------
#Colors Block
#------------------------------------------------------------------------------

class color:

    red = '\033[0;31m'
    green = '\033[0;32m'
    nc = '\033[0m' # No Color
    bold = '\033[1m'
    end= '\033[0m'

#------------------------------------------------------------------------------
#AWS Account Informations Block
#------------------------------------------------------------------------------

print ('\n' '- AWS Account Informations', '\n')

response = sts_client.get_caller_identity()
account = response['Account']
print('Account ID:', account)

response = iam_client.list_account_aliases()
alias = response['AccountAliases']
alias_account = ''.join(map(str, alias[0]))
print('Account Alias:', alias_account)

#------------------------------------------------------------------------------
#Input Block
#------------------------------------------------------------------------------

mode = input('\n'"Choose the script mode [create/partial_delete/complete_delete]: ")

if mode == "create":
    print ('\n' '- Backup Vault Informations''\n')
    backup_vault_name = input ("Backup Vault Name: ")
    print ('\n' '- Backup Plan Informations' '\n')
    backup_plan_name = input ("Backup Plan Name: ")
    rule_name = input ("Rule Name: ")
    schedule_cron_expression = input ("Schedule Cron Expression: ")
    backup_start_window = int(input ("Backup Start Window (Hours): "))
    backup_start_window_minutes = backup_start_window * 60
    backup_complete_window = int(input ("Backup Complete Window (Hours): "))
    backup_complete_window_minutes = backup_complete_window * 60
    backup_retention_period = int(input ("Backup Retention Period (Days): "))
    windows_vss = input ("Enable Windows VSS (only for EC2)? [enabled/disabled] : ")
    print ('\n' '- Backup Selection Parameters''\n')
    backup_selection_name = input ("Backup Selection Name: ")
    condition_key = input ("Condition Key: ")
    condition_value = input ("Condition Value: ")
elif mode == "partial_delete":
    backup_plan_name_delete = input ("Backup Plan Name: ")
elif mode == "complete_delete":
    backup_vault_name_delete = input ('\n'"Backup Vault Name: ")
else:
    print(color.red + "exited")
    exit()

#------------------------------------------------------------------------------
#AWS Backup Vault Block (create) / AWS Backup Selection Block (delete) 
#------------------------------------------------------------------------------

try:
    if mode == "create":
        response = kms_client.describe_key(
        KeyId='alias/aws/backup'
    )
        EncryptionKeyArn=response['KeyMetadata']['Arn']

        response = client.create_backup_vault(
            BackupVaultName=backup_vault_name,
            EncryptionKeyArn=EncryptionKeyArn
    )
    elif mode == "partial_delete":

        out = check_output(["aws", "backup", "list-backup-plans", "--query", "BackupPlansList[?BackupPlanName=='{}'].BackupPlanId".format(backup_plan_name_delete), "--output", "text"])
        str_data = out.decode('utf-8')
        data_arr=str_data.split()

        bpk_plan_id= ''.join(map(str, data_arr))

        response = client.list_backup_selections(
            BackupPlanId=bpk_plan_id
        )

        for backup in response['BackupSelectionsList']:
            SelectionId = backup['SelectionId']

            response = client.delete_backup_selection(
                BackupPlanId=bpk_plan_id,
                SelectionId=SelectionId
        )
    elif mode == "complete_delete":

        out = check_output(["aws", "backup", "list-backup-plans", "--query", "BackupPlansList[?BackupPlanName=='{}'].BackupPlanId".format(backup_plan_name_delete), "--output", "text"])
        str_data = out.decode('utf-8')
        data_arr=str_data.split()

        bpk_plan_id= ''.join(map(str, data_arr))

        response = client.list_backup_selections(
            BackupPlanId=bpk_plan_id
        )

        for backup in response['BackupSelectionsList']:
            SelectionId = backup['SelectionId']

            response = client.delete_backup_selection(
                BackupPlanId=bpk_plan_id,
                SelectionId=SelectionId
        )
    else:
        exit()
except client.exceptions.AlreadyExistsException as e:
    print('\n', color.red + "{} already exists. Try Again!".format(backup_vault_name) + color.end,'\n')
    sys.exit(1)

#------------------------------------------------------------------------------
#AWS Backup Plan Block (create & delete)
#------------------------------------------------------------------------------

if mode == "create":
    response = client.create_backup_plan(
    BackupPlan={
        'BackupPlanName': backup_plan_name,
        'Rules': [
            {
                'RuleName': rule_name,
                'TargetBackupVaultName': backup_vault_name,
                'ScheduleExpression': schedule_cron_expression,
                'StartWindowMinutes': backup_start_window_minutes,
                'CompletionWindowMinutes': backup_complete_window_minutes,
                'Lifecycle': {
                    'DeleteAfterDays': backup_retention_period
                },
            },
        ],
        'AdvancedBackupSettings': [
            {
                'ResourceType': 'EC2',
                'BackupOptions': {
                    'WindowsVSS': windows_vss
                }
            },
        ]
    },
)
    BackupPlanId = response['BackupPlanId']
    BackupPlanArn = response['BackupPlanArn']

    response = client.get_backup_plan(
    BackupPlanId=BackupPlanId
    )
    BackupPlanName = response['BackupPlan']['BackupPlanName']

elif mode == "partial_delete":
    response = client.delete_backup_plan(
    BackupPlanId=bpk_plan_id
)
elif mode == "complete_delete":
    response = client.delete_backup_plan(
    BackupPlanId=bpk_plan_id
)
else:
    exit()
#------------------------------------------------------------------------------
#AWS Backup Selection Block (create) / #AWS Backup Notification Block (delete) 
#------------------------------------------------------------------------------

if mode == "create":
    response = iam_client.get_role(
    RoleName='AWSBackupDefaultServiceRole'
)
    IamRoleArn = response['Role']['Arn']

    response = client.create_backup_selection(
    BackupPlanId= BackupPlanId,
    BackupSelection={
        'SelectionName': backup_selection_name,
        'IamRoleArn':IamRoleArn,

        'ListOfTags': [
            {
                'ConditionType': 'StringEquals',
                'ConditionKey': condition_key,
                'ConditionValue': condition_value
            },
        ]
    }
)

    SelectionId = response['SelectionId']

    response = client.get_backup_selection(
        BackupPlanId=BackupPlanId,
        SelectionId=SelectionId
    )
    SelectionName = response['BackupSelection']['SelectionName']

elif mode == "complete_delete":
    response = client.delete_backup_vault_notifications(
    BackupVaultName=backup_vault_name_delete
)
else:
    exit()
#------------------------------------------------------------------------------
#AWS Backup Notification Block (create) / AWS Backup Vault Block (delete)
#------------------------------------------------------------------------------

if mode == "create":
    response = sns_client.create_topic(
    Name='Security_and_Compliance_Topic'
)
    SNSTopic=response['TopicArn']

    response = client.put_backup_vault_notifications(
    BackupVaultName=backup_vault_name,
    SNSTopicArn=SNSTopic,
    BackupVaultEvents=[
        'BACKUP_JOB_FAILED',
    ]
)
    response = sns_client.subscribe(
    TopicArn=SNSTopic,
    Protocol='HTTPS',
    Endpoint='https://monitoring.solvimm.com',
    ReturnSubscriptionArn=False
)

    response = client.get_backup_vault_notifications(
    BackupVaultName=backup_vault_name
)
    BackupEvents=response['BackupVaultEvents']

elif mode == "complete_delete":
    response = client.delete_backup_vault(
    BackupVaultName=backup_vault_name_delete
)
else:
    exit()

#------------------------------------------------------------------------------
#Returns Block
#------------------------------------------------------------------------------

if mode == "create":
    print('\n''------------------------------------''\n', \
        color.green + "RESOURCES CREATED SUCCESSFULLY!"'\n', \
        color.nc + '------------------------------------''\n', \
        '\n'"- Backup Informations",'\n', \
        '\n'" Backup Vault Name: ",response['BackupVaultName'],'\n', \
        "Backup Vault Arn: ",response['BackupVaultArn'],'\n', \
        "Encryption Key Arn: ",EncryptionKeyArn,'\n', \
        "Backup Plan Name: ",BackupPlanName,'\n', \
        "Backup Plan ID: ",BackupPlanId,'\n',\
        "Backup Plan Arn: ",BackupPlanArn,'\n', \
        "Selection Name: ",SelectionName, '\n',\
        "Selection ID: ",SelectionId,'\n', \
        "IAM Role Arn: ",IamRoleArn,'\n', \
        "SNS Topic ARN: ",SNSTopic,'\n', \
        "Backup Job Events: ",BackupEvents,'\n')
elif mode == "partial_delete":
    print('\n''------------------------------------''\n', \
    color.green + "BACKUP PLAN & BACKUP SELECTION DELETED SUCCESSFULLY!"'\n', \
    color.nc + '------------------------------------''\n')
elif mode == "complete_delete":
    print('\n''------------------------------------''\n', \
    color.green + "ALL RESOURCES DELETED SUCCESSFULLY!"'\n', \
    color.nc + '------------------------------------''\n')
else:
    exit()