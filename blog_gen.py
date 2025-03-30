import boto3
import botocore.config
import json

from datetime import datetime

def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt=f"""<s>[INST]HUMAN: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]

    """
    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
        
    }
    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))
        response=bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-70b-instruct-v1:0")

        response_content = response.get('body').read().decode("utf-8")
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"error generating the code {e}")
        return ""

def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3=boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket,Key=s3_key,Body=generate_blog)
    except Exception as e:
        print("error saving code to s3")



def lambda_handler(event, context):
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']
    
    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)
    if generate_blog:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key = f"blog_output/{current_time}.txt"
        s3_bucket='roy-aws-bedrock-course'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)
    else:
        print("no blog was generated ")
    

    return {

        'StatusCode':200,
        'body':json.dumps('blog generation is completed ')
    }



     
