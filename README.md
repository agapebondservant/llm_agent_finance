# Financial Agent Support Bot
<div style="background-color:#EAFFF1; border: 1px solid lightgreen; padding: 30px">
NOTE: Originally forked from <a href="https://github.com/pdavis327/llm_agent_finance" target="_blank">this repo</a>.
</div>

This chatbot is part of a POC for a FSI use case.

## Getting Started

### Prerequisites

1. Clone the repository and navigate to the project directory:

   ```zsh
   git clone <repository-url>
   cd <repository-name>
   ```

2. Rename `.env.example` to  `.env`

3. Specify the environment parameters in the `.env` file.

## Executing the Program

### Creating a Chroma Database and Embedding Documents

To convert pdf to md using chrome run specify the input,output, and mode parameters when running `convert_pdf.py`

non ocr, default:

 ```zsh
python convert_pdf.py ./assets/library/documents ./assets/library/docling_out
 ```

 or if you want to do ocr
 
 ```zsh
python convert_pdf.py ./assets/library/documents ./assets/library/docling_out --mode ocr
 ```

 or if you have mac and want to do ocr
 
 ```zsh
python convert_pdf.py ./assets/library/documents ./assets/library/docling_out --mode mac_ocr
 ```

You can create a Chroma database and embed documents using `util/chroma.py`. It requires one argument: the filepath to the documents you wish to embed and store.

Run the following command:

```zsh
python util/chroma.py ./assets/library/docling_out
```

The results will be stored using your environment variables in a new Chroma database defined by `CHROMA_COLLECTION_NAME` and `CHROMA_PERSIST_PATH`.

### Running the Application locally

```zsh
podman-compose up
```

You should be able to view the app in your browser at the following URL:

```
http://0.0.0.0:8501
```

### Running the Application on Openshift

1. Generate streamlit-secret:

```zsh
oc delete secret streamlit-secret --ignore-not-found
oc create secret generic streamlit-secret --from-env-file=.env
```

2. Generate builds (requires write access):

```zsh
docker build -t quay.io/oawofolurh/finance_rag_assets -f Containerfile.chroma --platform linux/amd64 --push .
docker build -t quay.io/oawofolurh/finance-agent-ollama-container -f Containerfile.ollama --platform linux/amd64 --push .
docker build -t quay.io/oawofolurh/llm-agent-finance-streamlit-app -f Containerfile.streamlit --platform linux/amd64 --push .
```

3. Deploy app:

```zsh
oc apply -f k8s/
```

4. Create a route for the app:

```zsh
oc expose svc streamlit-app --port 8501
```

5. View the deployment to validate that there are no issues:

```zh
watch oc get all
```

6. The app should be accessible at the FQDN below:

```zh
oc get route streamlit-app -ojson | jq -r '.spec.host'
```

### Serving LLMs on Openshift AI
1. Install Minio: (see <a href="https://ai-on-openshift.io/tools-and-applications/minio/minio/#log-on-to-your-project-in-openshift-console" target="_blank">link</a>)

```zh
oc new-project minio --display-name="Minio S3 for LLMs"
oc apply -f k8s/minio/minio-all.yaml
python -m venv venv1
source venv1/bin/activate
pip install -r minio/minio-requirements.txt
HF_TOKEN='your huggingface token' MINIO_ACCESS_KEY='minio' MINIO_SECRET_KEY='minio123' MINIO_ENDPOINT=$(oc get route minio-api -ojson | jq -r '.spec.host') python minio/download_llms.py
deactivate
```
