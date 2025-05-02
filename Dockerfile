FROM python:3.11

# Required to install `sudachipy` (used by Coqui TTS)
ENV PATH=$PATH:/root/.cargo/bin
RUN curl https://sh.rustup.rs -sSf > /rust.sh && sh /rust.sh -y && rustup install stable

# Install system dependencies
RUN apt update && \
    apt upgrade -y && \
    apt install -y libsndfile1 ffmpeg

WORKDIR /app

# Copy requirements and Makefile
COPY ["requirements.txt", "Makefile", "./"]

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
RUN pip install --no-cache-dir google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Create TTS license acceptance file to avoid interactive prompts
RUN mkdir -p /root/.cache/coqui && \
    echo 'y' > /root/.cache/coqui/tts-license-agreement.txt

# Pre-download TTS model to avoid downloading it on every container start
RUN python -c "import os; os.environ['COQUI_TOS_AGREED']='1'; \
    import torch; \
    from TTS.api import TTS; \
    from TTS.tts.configs.xtts_config import XttsConfig; \
    from TTS.tts.configs.shared_configs import XttsAudioConfig; \
    from TTS.config.shared_configs import BaseDatasetConfig; \
    from TTS.utils.arguments import XttsArgs; \
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs]); \
    TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=True); \
    print('TTS model pre-downloaded successfully')"

# Copy application files
COPY configs.yaml .
COPY src/ src/
COPY api.py .

# Default command to run FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
