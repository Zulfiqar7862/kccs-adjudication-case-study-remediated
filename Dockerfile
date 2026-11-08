FROM python:3.12-slim
WORKDIR /app
COPY prototype ./prototype
RUN pip install --no-cache-dir ./prototype
CMD ["python","-m","adjudication.cli","run","--workbook","data/KCCS_Sentinel_Reference_Data_Pack.xlsx","--output-dir","prototype/output"]
