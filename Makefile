#=====================================================#
#                                                     #
#         BASE RPM BUILD FOR HAPROXY 1.8.X            #
#                                                     #
#=====================================================#

HOME=$(shell pwd)
VERSION=1.8
MINOR_VERSION=1.8.3
RELEASE=1

all: build

pre_req_setup:
	sudo yum install -y pcre-devel pcre-devel make gcc openssl-devel rpm-build

clean_build:
	rm -f ./SOURCES/haproxy-${VERSION}.tar.gz
	rm -rf ./rpmbuild
	mkdir -p ./rpmbuild/SPECS/ ./rpmbuild/SOURCES/ ./rpmbuild/RPMS/ ./rpmbuild/SRPMS/

ha_download:
	wget http://www.haproxy.org/download/${VERSION}/src/haproxy-${MINOR_VERSION}.tar.gz -O ./SOURCES/haproxy-${MINOR_VERSION}.tar.gz 

build: pre_req_setup clean_build ha_download
	cp -r ./SPECS/* ./rpmbuild/SPECS/ || true
	cp -r ./SOURCES/* ./rpmbuild/SOURCES/ || true
	rpmbuild -ba SPECS/haproxy.spec \
	--define "version ${VERSION}" \
	--define "release ${RELEASE}" \
	--define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}/BUILD" \
	--define "_buildroot %{_topdir}/BUILDROOT" \
	--define "_rpmdir %{_topdir}/RPMS" \
	--define "_srcrpmdir %{_topdir}/SRPMS"
