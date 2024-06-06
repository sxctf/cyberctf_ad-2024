FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY ./br-app/go.mod ./
RUN go mod download && go mod verify

COPY . ./