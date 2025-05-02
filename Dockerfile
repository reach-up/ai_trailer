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
COPY ["requirements.txt", "Makefile", "./"]
RUN pip install -r requirements.txt


RUN pip install fastapi uvicorn

COPY configs.yaml .
COPY src/ src/
COPY api.py .  

# ---------------------------------------------------------------
# `TTS` prompts the user to accept terms, here I donwload a model and agree with them
RUN yes | python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"
# ---------------------------------------------------------------


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
