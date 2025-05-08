## rag_chatbot_dav_6300_discussion_2
RAG Enabled Chatbot on AWS Bedrock : AV 6300 Discussion 2 Project: 

This is a solution for building a single interface conversational chatbot that allows end users to choose between different large language models (LLMs), inference parameters for varied input data formats. The solution uses Amazon Bedrock features to create choice & flexibility to improve user experience & compare the model outputs from different choices.

## Features

* Choice to select various Foundation Models/Large Language Models available within Amazon Bedrock
* Select the Inference parameters
* Choice of various Data source Inoput format like PDF, TXT, Web URL, Audio file, Image file (Scanned PDF) and Power Point document
* Uses Amazon Titan Embedding Model - amazon.titan-embed-text-v1 for Embedding generation
* User Interface is built using Streamlit
* FAISS is used as In-memory vector store
* Complete solution is deployable using Cloudformation template files.

## Usage

 1. Launch the application by running (First time after deploying the application using Cloudformation template) -

`cd $HOME/rag_chatbot_dav_6300_discussion_2
bucket_name=$(aws cloudformation describe-stacks --stack-name StreamlitAppServer --query "Stacks[0].Outputs[?starts_with(OutputKey, 'BucketName')].OutputValue" --output text)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
aws_region_name=$(curl -s http://169.254.169.254/latest/meta-data/placement/region -H "X-aws-ec2-metadata-token: $TOKEN")
sed -i "s/<S3_Bucket_Name>/${bucket_name}/g" $HOME/rag_chatbot_dav_6300_discussion_2/src/utils.py
sed -i "s/<AWS_Region>/${aws_region_name}/g" $HOME/rag_chatbot_dav_6300_discussion_2/src/utils.py
export AWS_DEFAULT_REGION=${aws_region_name}
streamlit run src/home.py`.

 2. For all subsequent launch - 

`cd $HOME/rag_chatbot_dav_6300_discussion_2
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
aws_region_name=$(curl -s http://169.254.169.254/latest/meta-data/placement/region -H "X-aws-ec2-metadata-token: $TOKEN")
export AWS_DEFAULT_REGION=${aws_region_name}
streamlit run src/home.py`

Instead you can use `start_program.sh` as a single bash file to launch 

3. Select the Large Language Model (LLM)
4. Select the Source Document Input
5. Q&A Tab is the defautl Tab (interface) - Start asking question related to the source document selected in 4th Step. 

    * You can download the chat history (downloaded as history.txt file)
    * You can "Clear" the chat history

6.  "Document Summary" is the 2nd Tab

    * You can create a nice summary for your uploaded document
    * Create Key Insights in bullete format for your uploaded document
    * Generate a 10 key questions from your uploaded document
    * You can even see the extracted "Text" from the uploaded document
    * For larger documents sumamrization (Token Size > 2500), solution is leverraging Anthropic Claude V2 model irrespective of what LLM you selected in Step 1 but for all other cases, LLM remains the same what you selected.

## Modules

* `home.py`:  Streamlit Application main file and the Entry point of the application
* `utils.py`: consists of all template, input and other utility functions of loki. You define all your metadata related to Amazon Bedrock LLM in this file viz. S3 Bucket Name, bucket prefix, AWS Region, Model name and Model ID.
* `loaders.py`: Contains utility functions for document loading, splitting and Chunking. Contains functions to create embeddings from text.
* `textgeneration.py`: Contains all the utility functions for generating Q&A response, summarization and key Sights - using Amazon Bedrock.
* `chat.py`: Contains utility functions for Conversational chat with the Application.

## Utility Functions

* `check_upload()`: Function to check if file has been uploaded
* `extract_data()`: Function to extract text from the uploaded files
* `create_embeddings()`: Function to create embeddings from text
* `num_tokens_from_string()`: Function to count number of tokens in a text string.
* `check_job_name()`: Function to check the Amazon Transcribe job status.
* `amazon_transcribe()`: Function to invoke Amazon Transcribe job.
* `upload_audio_file_s3()`: Function to upload Audio file to Amazon S3 Bucket.
* `initialize_summary_session_state()`: Function to initialize the session state variables.
* `bedrock_llm_call()`: Function to instantiate various LLM call within Amazon Bedrock service.
* `q_response()`: Function to generate the response agains the User Input within the Application.
* `search_context()`: Function to search the vector database(FAISS here) for the most similar section to the user question.
* `summarizer()`: Function to create the summary of each individual chunk as well as the final summary.
* `summary()`: Function to generate a summary of a document - invoked from the main streamlit Application module.
* `talking()`: Function to generate key points of a document - invoked from the main streamlit Application module.
* `questions()`: Function to generate questions from a document - invoked from the main streamlit Application module.

## Configuration File

* `config.ini` - Contains logo, images and greeting message for the look and feel of the Streamlit application. 

## Setup Files

* `ALB_Setup_for_Chatbot.yml`: Cloudformation YAML Template for Streamlit Deployment in Public Subnet
* `ALB_Setup_for_Chatbot_Private_Gateway.yml`: Cloudformation YAML Template for Streamlit Deployment in Private Subnet with NAT Gateway


