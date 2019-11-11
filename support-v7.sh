#!/usr/bin/env bash
python pompom.py \
	--project-name support-v7-27.0.2 \
	--pom https://maven.google.com/com/android/support/cardview-v7/27.0.2/cardview-v7-27.0.2.pom \
	--pom https://maven.google.com/com/android/support/appcompat-v7/27.0.2/appcompat-v7-27.0.2.pom \
	--exclude out/support-v4-27.0.2/dependencies.json \
	-apv 28 \
	poms deps zip
