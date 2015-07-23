#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum_1=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
sha1sum_2=$(tig commit "Added goodbye world.")
tig checkout -b mybranch ${sha1sum_1}

echo '0a
Branched World
.
w' | ed file.txt 2> /dev/null
sha1sum_3=$(tig commit "Added branched world.")

tig checkout master > /dev/null
tig merge mybranch > /dev/null

cat > ${tdir}/expected.txt <<EOF
Branched World
Hello World
Goodbye World
EOF

if diff -u ${tdir}/expected.txt file.txt; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
