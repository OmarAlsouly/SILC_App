in Anaconda Prompt:
1.
to create virt env run > 
conda create --name projectFlask python=3.9.5
to activate virt env run > 
activate projectFlask

virtual env needs to be created only once, and reactivated every time you launch anaconda prompt.

2. installing pre reqs in the virt env, only need to be done once.
pip install -r requirements.txt

3. to run the app:
flask run
