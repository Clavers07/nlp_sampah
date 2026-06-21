
REQUIREMENT
1. uvicorn

HOW TO RUN
1. Run Anaconda Prompt AS ADMINISTRATOR
2. Activate env with 'conda activate yourenv'
3. change directory to project root by 'cd C:\coding\kep python\nlp_sampah'
4. Run server with 'uvicorn main:app --reload'
5. Wait till server completed and shows log as:
(yoloenv) C:\Windows\System32>cd C:\coding\kep python\nlp_sampah

(yoloenv) C:\coding\kep python\nlp_sampah>uvicorn main:app --reload
←[32mINFO←[0m:     Will watch for changes in these directories: ['C:\\coding\\kep python\\nlp_sampah']
Loading weights: 100%|████████████████████████████████████████████████████████████| 293/293 [00:00<00:00, 18240.98it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [22600] using StatReload
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|████████████████████████████████████████████████████████████| 293/293 [00:00<00:00, 21755.61it/s]
INFO:     Started server process [4648]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
