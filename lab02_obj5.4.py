import boto3
import time
import smtplib

print('Entering an infinite loop of process, Please press ^C to exit the program anytime......\n\n\n')
while(1):
    print('Checking the running instances in EC2 AWS..........')
    ins1=[]
    ins2=[]
    probs=[]
    z=0
    st=[]
    alarm_st=[]
        
    #Gathering IDs of running instances
    ec2=boto3.resource('ec2')
    instances=ec2.instances.filter(Filters=[{'Name':'instance-state-name','Values':['running']}])
    for instance in instances:
        print(instance.id,' [running]')
        ins1.append(instance.id)
        
        
    print("Total running instances detected =>",len(ins1))
        
    #connecting to the AWS CloudWatch
    cloudwatch = boto3.client('cloudwatch',region_name='us-west-1',aws_access_key_id="AKIAI3G6HM37ICXEOKTQ",aws_secret_access_key="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")
        
    for x in ins1:
        cloudwatch.put_metric_alarm(
                AlarmName='Anomaly:'+str(z),
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='CPUUtilization',
                Namespace='AWS/EC2',
                Period=60,
                Statistic='Average',
                Threshold=0.3,
                AlarmDescription='Alarm when server CPU exceeds 0.3%',
                ActionsEnabled=True,
                Dimensions=[
                    {
                      'Name': 'InstanceId',
                      'Value': x
                    },
                ],
                InsufficientDataActions=['arn:aws:automate:us-west-1:ec2:stop'],            
            )
        z=z+1
            
    #putting sleep for 10 minutes to let the new instances spin up
    print('Waiting for 10 minutes to let the anomaly occur')
    time.sleep(600)
    print('done')
    ec2=boto3.resource('ec2')
    for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
        ins2.append(status['InstanceId'])
        
    print("Total instances running before operations =>",len(ins1))
    print("Total instances running after operations =>",len(ins2))
    print("Number of new instances needed =>",len(ins1)-len(ins2))
        
    #finding instances that had higher utilization
    probs=list(set(ins1) - set(ins2))
        
    #sending notification about the higher utilization
    
    fromaddr="netmanlab007@gmail.com"
    toaddrs="rath4418@colorado.edu"
    #SMTP Used for sending notifications    
    server=smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    username="netmanlab007@gmail.com"
    password="netman@007"
    server.login(username,password)
        
    for x in probs:
        msg="Instance {} had Anomaly detected! so it is stopped and new resource is spun automatically. Please check.".format(x)
        server.sendmail(fromaddr,toaddrs,msg)
    print("Mail has been sent regarding the notifications.")
    server.quit()
        
    ec2.create_instances(ImageId='ami-0ad16744583f21877', MinCount=1, MaxCount=(len(ins1)-len(ins2)))
    print('Creating new instances....................Please wait')
    #putting sleep for 5 minutes, so that the script will wait for 5 minutes
    time.sleep(300)
