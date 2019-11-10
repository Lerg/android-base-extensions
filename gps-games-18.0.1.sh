#!/usr/bin/env bash
python pompom.py \
	--project-name gps-games-18.0.1 \
	--pom https://maven.google.com/com/google/android/gms/play-services-games/18.0.1/play-services-games-18.0.1.pom \
	--pom https://maven.google.com/com/google/android/gms/play-services-drive/17.0.0/play-services-drive-17.0.0.pom \
	--pom https://maven.google.com/com/google/android/gms/play-services-auth/17.0.0/play-services-auth-17.0.0.pom \
	--exclude out/gps-base-17.0.0/dependencies.json \
	-apv 28 \
	poms deps zip
