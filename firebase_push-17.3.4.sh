#!/usr/bin/env bash
python pompom.py \
	--project-name firebase_push-17.3.4 \
	--pom https://maven.google.com/com/google/firebase/firebase-messaging/17.3.4/firebase-messaging-17.3.4.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	--exclude out/firebase_core-16.0.7/dependencies.json \
	-apv 28 \
	poms deps zip
