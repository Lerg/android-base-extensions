#!/usr/bin/env bash
python pompom.py \
	--project-name gps-ads-17.2.1 \
	--pom https://maven.google.com/com/google/android/gms/play-services-ads/17.2.1/play-services-ads-17.2.1.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	--exclude out/support-v4-27.0.2/dependencies.json \
	-apv 28 \
	poms deps zip
