#!/usr/bin/env bash
python pompom.py \
	--project-name firebase-core-16.0.7 \
	--pom https://maven.google.com/com/google/firebase/firebase-core/16.0.7/firebase-core-16.0.7.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	--exclude out/gps-ads-17.2.1/dependencies.json \
	-apv 28 \
	poms deps zip

python pompom.py \
	--project-name firebase-core-16.0.9 \
	--pom https://maven.google.com/com/google/firebase/firebase-core/16.0.9/firebase-core-16.0.9.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	--exclude out/gps-ads-17.2.1/dependencies.json \
	-apv 28 \
	poms deps zip
