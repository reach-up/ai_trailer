FROM python:3.11

# ---------------------------------------------------------------
# Required to install `sudachipy` a requirement from `TTS`
ENV PATH=$PATH:/root/.cargo/bin
RUN curl https://sh.rustup.rs -sSf > /rust.sh && sh /rust.sh -y \
    && rustup install stable
# ---------------------------------------------------------------
# Required to install `libsndfile1` and `ffmpeg` for audio processing
RUN apt update && \
    apt upgrade -y && \
    apt install -y libsndfile1 ffmpeg
# ---------------------------------------------------------------

WORKDIR /app

# Copy service account key for Google Drive API
COPY service_account.json .

# Copy requirements and Makefile
COPY ["requirements.txt", "Makefile", "./"]

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
RUN pip install --no-cache-dir google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Copy application code
COPY configs.yaml .
COPY src/ src/
COPY api.py .  

# ---------------------------------------------------------------
# Run the FastAPI server
# ---------------------------------------------------------------
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
