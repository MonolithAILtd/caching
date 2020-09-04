#!/usr/bin/env bash
docker login -u AWS -p $(aws ecr get-login-password) https://376730970890.dkr.ecr.eu-west-2.amazonaws.com ||
$(aws ecr get-login --no-include-email)
