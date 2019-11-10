#!/usr/bin/env bash
python pompom.py \
	--project-name facebook-5.9.0 \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-core/5.9.0/facebook-core-5.9.0.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-login/5.9.0/facebook-login-5.9.0.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-share/5.9.0/facebook-share-5.9.0.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-applinks/5.9.0/facebook-applinks-5.9.0.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-places/5.9.0/facebook-places-5.9.0.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-messenger/5.9.0/facebook-messenger-5.9.0.pom \
	--exclude out/support-v4-27.0.2/dependencies.json \
	--exclude out/support-v7-27.0.2/dependencies.json \
	-apv 28 \
	poms deps zip
