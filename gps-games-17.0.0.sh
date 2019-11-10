#!/usr/bin/env bash
python pompom.py \
	--project-name gps-games-17.0.0 \
	--pom https://maven.google.com/com/google/android/gms/play-services-games/17.0.0/play-services-games-17.0.0.pom \
	--pom https://maven.google.com/com/google/android/gms/play-services-drive/16.0.0/play-services-drive-16.0.0.pom \
	--pom https://maven.google.com/com/google/android/gms/play-services-auth/16.0.0/play-services-auth-16.0.0.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	-apv 28 \
	poms deps zip
