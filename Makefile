.PHONY: all  run gotool clean help x86 arm docker
# --platform linux/arm/v8 
docker:
	docker build -t wencai . 

save:
	docker save -o wencai.tar wencai:latest