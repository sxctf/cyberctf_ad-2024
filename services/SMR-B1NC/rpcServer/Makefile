PHONY: generate-struct
generate-struct:
	mkdir -p pkg/
	protoc --go_out=pkg/ \
	--go-grpc_out=pkg/ \
	proto/smartbalance.proto

