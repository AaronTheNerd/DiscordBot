PY = python3.8
PIP = pip
VENV = pipenv

.PHONY: connect run setup-venv shell clean

connect:
	ssh -i discord-bot.pem ubuntu@ec2-34-228-160-153.compute-1.amazonaws.com

run:
	$(VENV) run $(PY) src/bot.py

setup-venv:
	$(PIP) install $(VENV)
	$(VENV) install

shell:
	$(VENV) shell

clean:
	rm logs/*.log 
