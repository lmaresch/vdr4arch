# This PKGBUILD could be part of the VDR4Arch project [https://github.com/vdr4arch]

pkgname=vdr-vaapidevice
pkgver=0.7.0.r205.ga17c110
_gitver=d19657bae399e79df107e316ca40922d21393f80
_vdrapi=2.4.1
pkgrel=3
pkgdesc="A VA-API output device plugin for VDR"
url="https://github.com/pesintta/vdr-plugin-vaapidevice"
arch=('x86_64' 'i686' )
license=('GPL2')
depends=("vdr-api=${_vdrapi}")
_plugname=${pkgname//vdr-/}
source=("vdr-plugin-${_plugname}::git+https://github.com/pesintta/vdr-plugin-vaapidevice#commit=$_gitver"
        "50-$_plugname.conf")
backup=("etc/vdr/conf.avail/50-$_plugname.conf")
sha512sums=('SKIP'
         'd33b7698126e39d11c1246096f99235ef20edcdecad0b40ae46d4415bf344c75c97434a495b1ad90cd7d7b52bdfe78b756a97d850224d24d06a445d7e580532f')

pkgver() {
    cd "${srcdir}/vdr-plugin-${_plugname}"
    git describe --long --tags | sed 's/\([^-]*-g\)/r\1/;s/-/./g;s/^v//'

}

prepare() {
    cd "${srcdir}/vdr-plugin-${_plugname}"
}

build() {
    cd "${srcdir}/vdr-plugin-${_plugname}"
    make
}

package() {
    cd "${srcdir}/vdr-plugin-${_plugname}"
    make DESTDIR="${pkgdir}" install

    install -Dm644 "$srcdir/50-$_plugname.conf" "$pkgdir/etc/vdr/conf.avail/50-$_plugname.conf"
}
