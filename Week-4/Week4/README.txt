WEEK 4 - TOKENIZER LAB
Comparison of BPE, WordPiece and SentencePiece
Languages: English, Telugu and Hindi

FILES
- tokenizer_comparison.py: Main program
- requirements.txt: Required libraries

RUN ON WINDOWS USING VS CODE
1. Extract this ZIP.
2. Open VS Code -> File -> Open Folder -> Week4_Tokenizer_Lab.
3. Open Terminal -> New Terminal. Confirm terminal is inside this folder.
4. Create a virtual environment:
   py -m venv .venv
5. Activate it in PowerShell:
   .venv\\Scripts\\Activate.ps1
   If activation is blocked, run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .venv\\Scripts\\Activate.ps1
6. Install libraries:
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
7. Run:
   python tokenizer_comparison.py

Internet access is required on the first run to download pretrained tokenizer files.
The first run may take a few minutes.

The program compares:
- GPT-2: byte-level BPE
- bert-base-multilingual-cased: WordPiece
- xlm-roberta-base: SentencePiece framework using a BPE model

It prints token pieces, token IDs and token counts for all three languages.
Actual outputs depend on the downloaded pretrained tokenizer files.
