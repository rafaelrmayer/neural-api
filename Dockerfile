FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 1000 appuser
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu 'torch>=2.5,<3.0' \
    && python -m pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser scripts ./scripts
USER appuser
RUN python -m scripts.train_cards_demo --output /home/appuser/modelo_cartoes_demo.pt
ENV CARDS_MODEL_PATH=/home/appuser/modelo_cartoes_demo.pt
ENV CORS_ALLOWED_ORIGINS=https://rafaelrmayer.github.io
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
