PY = python3.8
PIP = pip
VENV = pipenv

.PHONY: run setup-venv shell clean

run:
	$(VENV) run $(PY) discord_bot/bot.py

setup-venv:
	$(PIP) install $(VENV)
	$(VENV) install

shell:
	$(VENV) shell

clean:
	rm logs/*.log 
