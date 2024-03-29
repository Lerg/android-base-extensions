#!/usr/bin/env bash
python pompom.py \
	--project-name facebook-5.0.1 \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-core/5.0.1/facebook-core-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-login/5.0.1/facebook-login-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-share/5.0.1/facebook-share-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-applinks/5.0.1/facebook-applinks-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-places/5.0.1/facebook-places-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-messenger/5.0.1/facebook-messenger-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/facebook-android-sdk/5.0.1/facebook-android-sdk-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/audience-network-sdk/5.0.1/audience-network-sdk-5.0.1.pom \
	--pom http://central.maven.org/maven2/com/facebook/android/account-kit-sdk/5.0.0/account-kit-sdk-5.0.0.pom \
	--exclude out/gps-base-16.0.1/dependencies.json \
	-apv 28 \
	poms deps zip
