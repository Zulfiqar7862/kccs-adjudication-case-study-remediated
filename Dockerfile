FROM python:3.12-slim
WORKDIR /app
COPY prototype/requirements.txt ./prototype/requirements.txt
RUN pip install --no-cache-dir -r prototype/requirements.txt
COPY prototype ./prototype
WORKDIR /app/prototype
CMD ["python","-m","adjudication.cli","run","--workbook","../data/KCCS_Sentinel_Reference_Data_Pack.xlsx","--output-dir","output"]
