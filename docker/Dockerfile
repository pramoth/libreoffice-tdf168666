# syntax=docker/dockerfile:1.7
#
# Builds LibreOffice (headless) twice from the same tree: as released, and with the tdf#168666 fix.
#
#   docker build --target lo-unpatched -t lo-tdf168666:unpatched -f docker/Dockerfile .
#   docker build --target lo-patched   -t lo-tdf168666:patched   -f docker/Dockerfile .
#
# The first build takes 30-60 min with 12 cores (ccache is kept in a BuildKit cache mount);
# the patched one only recompiles sw/source/core/txtnode/fntcache.cxx.

ARG LO_TAG=libreoffice-26.8.2.2

FROM debian:13 AS lo-build-env
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf automake bison build-essential ca-certificates ccache cmake curl flex fontconfig \
        gettext git gperf libfontconfig-dev libfreetype-dev libkrb5-dev libnss3-dev libtool \
        libtool-bin libxml2-utils libxslt1-dev meson nasm ninja-build patch pkg-config python3 \
        python3-dev python3-setuptools unzip wget xsltproc zip zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
# LibreOffice refuses to build as root
RUN useradd -m -u 1000 builder && mkdir -p /build /ccache && chown builder:builder /build /ccache
ENV CCACHE_DIR=/ccache CCACHE_MAXSIZE=30G
USER builder

FROM lo-build-env AS lo-unpatched
ARG LO_TAG
RUN git clone --depth 1 --branch ${LO_TAG} https://git.libreoffice.org/core /build/core
WORKDIR /build/core
# Based on distro-configs/LibreOfficeOnline.conf (headless), minus LTO and extra languages
RUN ./autogen.sh \
        --with-parallelism=12 \
        --disable-gui --disable-gtk3 --disable-qt5 --disable-kf5 \
        --disable-cups --disable-dbus --disable-dconf --disable-gio --disable-gstreamer-1-0 \
        --disable-epm --disable-evolution2 --disable-ext-nlpsolver --disable-ext-wiki-publisher \
        --disable-firebird-sdbc --disable-postgresql-sdbc --disable-mariadb-sdbc \
        --disable-odk --disable-online-update --disable-skia --disable-report-builder \
        --disable-scripting-beanshell --disable-scripting-javascript \
        --disable-sdremote --disable-sdremote-bluetooth \
        --disable-pdfimport --disable-pdfium --disable-poppler --disable-cve-tests \
        --enable-cairo-rgba --enable-mergelibs --enable-python=no \
        --with-fonts --with-galleries=no --with-theme=colibre \
        --without-branding --without-help --without-java --without-junit \
        --without-myspell-dicts --without-doxygen --without-package-format \
        --without-system-cairo --without-system-jars --without-system-jpeg \
        --without-system-libpng --without-system-libxml --without-system-openssl \
        --without-system-postgresql --with-system-zlib
RUN --mount=type=cache,target=/ccache,uid=1000,gid=1000 make build

FROM lo-unpatched AS lo-patched
COPY --chown=builder:builder patch/fix-only.patch /build/fix.patch
RUN git apply -p1 /build/fix.patch
RUN --mount=type=cache,target=/ccache,uid=1000,gid=1000 make build
