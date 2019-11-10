#!/usr/bin/env bash
python pompom.py \
	--project-name firebase_analytics-16.0.5 \
	--pom https://maven.google.com/com/google/firebase/firebase-analytics/16.0.5/firebase-analytics-16.0.5.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	--exclude out/firebase_core-16.0.7/dependencies.json \
	-apv 28 \
	poms deps zip
