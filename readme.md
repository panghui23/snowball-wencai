python -m venv venv
source venv/bin/activate  # 在 Linux 和 macOS


#docker保存

docker save -o wencai.tar wencai:latest

#docker解压
docker load -i wencai.tar
