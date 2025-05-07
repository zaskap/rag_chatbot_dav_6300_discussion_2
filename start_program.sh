#!/bin/bash

# Navigate to project directory
cd "$HOME/rag_chatbot_dav_6300_discussion_2" || exit

# Get S3 bucket name from CloudFormation stack output
bucket_name=$(aws cloudformation describe-stacks \
  --stack-name StreamlitAppServer \
  --query "Stacks[0].Outputs[?starts_with(OutputKey, 'BucketName')].OutputValue" \
  --output text)

# Get EC2 metadata token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Get AWS region
aws_region_name=$(curl -s http://169.254.169.254/latest/meta-data/placement/region \
  -H "X-aws-ec2-metadata-token: $TOKEN")

# Replace placeholders in utils.py
sed -i "s/<S3_Bucket_Name>/${bucket_name}/g" "$HOME/rag_chatbot_dav_6300_discussion_2/src/utils.py"
sed -i "s/<AWS_Region>/${aws_region_name}/g" "$HOME/rag_chatbot_dav_6300_discussion_2/src/utils.py"

# Export region for AWS CLI usage
export AWS_DEFAULT_REGION="${aws_region_name}"

# Start Streamlit app
streamlit run src/home.py
