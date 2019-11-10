#!/usr/bin/env bash
# https://developers.google.com/android/guides/setup

python pompom.py \
	--project-name gps-base-16.0.1 \
	--pom https://maven.google.com/com/google/android/gms/play-services-base/16.0.1/play-services-base-16.0.1.pom \
	--exclude out/support-v4-27.0.2/dependencies.json \
	-apv 28 \
	poms deps zip
