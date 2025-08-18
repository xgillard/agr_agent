:

VERSION=20250818.133325-develop-11a13de

mkdir -p $(pwd)/corpus/label-studio/data/media
mkdir -p $(pwd)/corpus/label-studio/data/test_data
mkdir -p $(pwd)/corpus/label-studio/data/export

chmod -R 777 $(pwd)/corpus/label-studio

docker run -it                              \
	-p 8080:8080                        \
	-v $(pwd)/corpus/label-studio/data:/label-studio/data \
	heartexlabs/label-studio:$VERSION   \
	label-studio

