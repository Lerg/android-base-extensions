#!/usr/bin/env bash
python pompom.py \
	--project-name androidx-1.0.0 \
	--pom https://maven.google.com/androidx/appcompat/appcompat/1.0.0/appcompat-1.0.0.pom \
	-apv 28 \
	poms deps zip
