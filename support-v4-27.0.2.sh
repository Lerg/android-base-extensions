!/usr/bin/env bash
python pompom.py \
	--project-name support-v4-27.0.2 \
	--pom https://maven.google.com/com/android/support/support-v4/27.0.2/support-v4-27.0.2.pom \
	--pom https://maven.google.com/com/android/support/customtabs/27.0.2/customtabs-27.0.2.pom \
	-apv 28 \
	poms deps zip
