# Financial Agent Support Bot

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
python convert_pdf.py ./assets/library/ocr_test ./assets/library/docling_out/ocr
 ```

 or if you want to do ocr
 ```zsh
python convert_pdf.py ./assets/library ./assets/library/docling_out --mode ocr
 ```

 or if you have mac and want to do ocr
 ```zsh
python convert_pdf.py ./assets/library ./assets/library/docling_out --mode mac_ocr
 ```

You can create a Chroma database and embed documents using `util/chroma.py`. It requires one argument: the filepath to the documents you wish to embed and store.

Run the following command:

```zsh
python util/chroma.py ./assets/library
```

The results will be stored using your environment variables in a new Chroma database defined by `CHROMA_COLLECTION_NAME` and `CHROMA_PERSIST_PATH`.

### Running the Application

```zsh
docker-compose up
```

You should be able to view the app in your browser at the following URL:

```
http://0.0.0.0:8501
```
