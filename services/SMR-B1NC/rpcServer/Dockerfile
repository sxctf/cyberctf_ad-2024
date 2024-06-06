FROM golang:1.21.9-alpine3.19 AS builder


WORKDIR /grpc_app

COPY go.mod ./
RUN go mod download && go mod verify
RUN apk add bash
RUN rm -rf /var/lib/apt/lists/*

COPY . ./
