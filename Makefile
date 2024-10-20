.PHONY: all  run gotool clean help x86 arm docker
# --platform linux/arm/v8 
docker:
	docker build --platform linux/amd64 -t wencai . 

save:
	docker save -o wencai.tar wencai:latest