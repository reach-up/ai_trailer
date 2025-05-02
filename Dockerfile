FROM python:3.11

# ---------------------------------------------------------------
# Required to install `sudachipy` a requirement from `TTS`
ENV PATH=$PATH:/root/.cargo/bin
RUN curl https://sh.rustup.rs -sSf > /rust.sh && sh /rust.sh -y \
    && rustup install stable
# ---------------------------------------------------------------
# Required to install `libsndfile1` a requirement from `TTS`
RUN apt update && \
    apt upgrade -y && \
    apt install -y libsndfile1 && \
    apt install -y ffmpeg
# ---------------------------------------------------------------

WORKDIR /app

# Copy requirements and Makefile
COPY ["requirements.txt", "Makefile", "./"]

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn

# Copy remaining files
COPY configs.yaml .
COPY src/ src/
COPY api.py .  

# ---------------------------------------------------------------
# Removed broken TTS preload step (model will load at runtime)
# ---------------------------------------------------------------

# Run API server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
