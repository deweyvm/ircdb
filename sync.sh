NAME=starstats
cp -a dist/build/$NAME/$NAME /usr/lib/cgi-bin
chmod a+x /usr/lib/cgi-bin/$NAME
cp -a generate.cgi /usr/lib/cgi-bin
chmod a+r /usr/lib/cgi-bin/generate.cgi
chmod a+x /usr/lib/cgi-bin/generate.cgi
mkdir -p /var/www/starstats
cp -a site/* \
      /var/www/starstats
chmod a+r /var/www/starstats/*
