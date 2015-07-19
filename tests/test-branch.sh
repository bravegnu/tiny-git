#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
tig commit "Added goodbye world." > /dev/null
tig checkout ${sha1sum} -b mybranch

tig branch >> ${tdir}/branches.txt
cat > ${tdir}/expected.txt <<EOF
 master
*mybranch
EOF

if diff -u ${tdir}/branches.txt ${tdir}/expected.txt; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
