.PHONY: all  run gotool clean help x86 arm docker
# --platform linux/arm/v8 
docker:
	docker build --platform linux/amd64 -t wencai . 
	docker save -o wencai.tar wencai:latest

save:
	docker save -o wencai.tar wencai:latest
#生成requirment
requirement:
	pip freeze > requirements.txt
venv:
	python -m venv venv
exit:
	deactivate
install:
	pip install -r requirements.txt
source:
	source ./venv/bin/activate
run:
	python main.py